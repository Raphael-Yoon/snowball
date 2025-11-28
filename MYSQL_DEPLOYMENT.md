# MySQL 운영서버 배포 가이드

## 개요

Snowball 시스템은 개발환경에서는 SQLite를 사용하지만, 운영서버는 MySQL을 사용합니다.
따라서 SQLite 마이그레이션 스크립트를 MySQL 버전으로 변환하여 실행해야 합니다.

---

## 배포 전 준비사항

### 1. 데이터베이스 백업 (필수!)

```bash
# 운영서버에서 실행
mysqldump -u사용자명 -p데이터베이스명 > backup_$(date +%Y%m%d_%H%M%S).sql

# 백업 파일 확인
ls -lh backup_*.sql
```

### 2. MySQL 버전 확인

```bash
mysql --version
```

**중요**: MySQL 5.7과 8.0에서 SQL 문법이 다릅니다!
- MySQL 8.0 이상: `IF NOT EXISTS`, `IF EXISTS` 문법 지원
- MySQL 5.7 이하: 개별 ALTER 문 실행 필요

---

## 배포 방법 1: 단계별 수동 실행 (권장)

### Step 1: 서버 접속 및 파일 업로드

```bash
# 서버 접속
ssh itap@운영서버주소

# snowball 디렉토리로 이동
cd /home/itap/snowball

# 최신 코드 가져오기
git pull origin main
```

### Step 2: MySQL 접속

```bash
mysql -u사용자명 -p
```

MySQL 프롬프트에서:

```sql
-- 데이터베이스 선택
USE 데이터베이스명;

-- 현재 테이블 구조 확인
DESCRIBE sb_rcm;
DESCRIBE sb_evaluation_sample;
```

### Step 3: 마이그레이션 실행

#### Option A: 단계별 스크립트 파일 실행

```bash
# MySQL 프롬프트에서
source /home/itap/snowball/migrations/mysql_migration_step_by_step.sql
```

각 STEP을 하나씩 실행하면서 결과를 확인하세요!

#### Option B: 수동으로 하나씩 실행

가장 안전한 방법입니다. 각 명령을 복사해서 하나씩 실행:

```sql
-- 1. upload_user_id를 user_id로 변경
ALTER TABLE sb_rcm
CHANGE COLUMN upload_user_id user_id INT NOT NULL;

-- 확인
DESCRIBE sb_rcm;

-- 2. sb_evaluation_sample 백업
CREATE TABLE sb_evaluation_sample_backup
SELECT * FROM sb_evaluation_sample;

-- 3. attribute 컬럼 추가 (MySQL 8.0+)
ALTER TABLE sb_evaluation_sample
  ADD COLUMN IF NOT EXISTS attribute0 TEXT,
  ADD COLUMN IF NOT EXISTS attribute1 TEXT,
  ADD COLUMN IF NOT EXISTS attribute2 TEXT,
  ADD COLUMN IF NOT EXISTS attribute3 TEXT,
  ADD COLUMN IF NOT EXISTS attribute4 TEXT,
  ADD COLUMN IF NOT EXISTS attribute5 TEXT,
  ADD COLUMN IF NOT EXISTS attribute6 TEXT,
  ADD COLUMN IF NOT EXISTS attribute7 TEXT,
  ADD COLUMN IF NOT EXISTS attribute8 TEXT,
  ADD COLUMN IF NOT EXISTS attribute9 TEXT;

-- MySQL 5.7이면 각각 실행:
-- ALTER TABLE sb_evaluation_sample ADD COLUMN attribute0 TEXT;
-- ALTER TABLE sb_evaluation_sample ADD COLUMN attribute1 TEXT;
-- ... (attribute2~9도 동일)

-- 4. evaluation_type 컬럼 추가 (없으면)
ALTER TABLE sb_evaluation_sample
ADD COLUMN IF NOT EXISTS evaluation_type VARCHAR(20) DEFAULT 'operation';

-- 5. no_occurrence 필드 추가
ALTER TABLE sb_design_evaluation_line
  ADD COLUMN IF NOT EXISTS no_occurrence TINYINT DEFAULT 0,
  ADD COLUMN IF NOT EXISTS no_occurrence_reason TEXT;

ALTER TABLE sb_design_evaluation_header
  ADD COLUMN IF NOT EXISTS no_occurrence_count INT DEFAULT 0;

-- 6. 최종 확인
DESCRIBE sb_rcm;
DESCRIBE sb_evaluation_sample;
DESCRIBE sb_design_evaluation_line;
```

### Step 4: 애플리케이션 재시작

```bash
# MySQL 종료
exit

# 애플리케이션 재시작
sudo systemctl restart snowball
# 또는
supervisorctl restart snowball

# 로그 확인
tail -f /var/log/snowball.log
# 또는
journalctl -u snowball -f
```

---

## 배포 방법 2: 일괄 실행 (주의 필요)

**주의**: 테스트 환경에서 먼저 실행해보고, 문제없을 때만 운영에 적용하세요!

```bash
mysql -u사용자명 -p데이터베이스명 < migrations/mysql_migration.sql
```

---

## MySQL 5.7 사용자를 위한 개별 실행 스크립트

MySQL 5.7은 `IF NOT EXISTS`를 지원하지 않으므로 개별로 실행:

```sql
-- 1. sb_rcm 테이블 변경
ALTER TABLE sb_rcm CHANGE COLUMN upload_user_id user_id INT NOT NULL;

-- 2. sb_evaluation_sample에 attribute 컬럼 추가
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute0 TEXT;
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute1 TEXT;
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute2 TEXT;
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute3 TEXT;
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute4 TEXT;
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute5 TEXT;
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute6 TEXT;
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute7 TEXT;
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute8 TEXT;
ALTER TABLE sb_evaluation_sample ADD COLUMN attribute9 TEXT;

-- 3. evaluation_type 컬럼 추가
ALTER TABLE sb_evaluation_sample ADD COLUMN evaluation_type VARCHAR(20) DEFAULT 'operation';

-- 4. no_occurrence 필드 추가
ALTER TABLE sb_design_evaluation_line ADD COLUMN no_occurrence TINYINT DEFAULT 0;
ALTER TABLE sb_design_evaluation_line ADD COLUMN no_occurrence_reason TEXT;
ALTER TABLE sb_design_evaluation_header ADD COLUMN no_occurrence_count INT DEFAULT 0;
```

---

## 트러블슈팅

### 문제 1: "Duplicate column name" 에러

**원인**: 컬럼이 이미 존재함

**해결**: MySQL 8.0이면 `IF NOT EXISTS` 사용, 5.7이면 무시하고 진행

```sql
-- 어떤 컬럼이 이미 있는지 확인
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'sb_evaluation_sample'
  AND COLUMN_NAME LIKE 'attribute%';
```

### 문제 2: "Unknown column 'upload_user_id'" 에러

**원인**: 이미 user_id로 변경되어 있음

**해결**: 다음 단계로 진행

```sql
-- 현재 컬럼명 확인
DESCRIBE sb_rcm;
```

### 문제 3: 트랜잭션 롤백 필요

```sql
-- 문제 발생 시 롤백
ROLLBACK;

-- 백업에서 복원
DROP TABLE sb_evaluation_sample;
CREATE TABLE sb_evaluation_sample SELECT * FROM sb_evaluation_sample_backup;
```

---

## 배포 후 확인사항

### 1. 테이블 구조 확인

```sql
-- 주요 테이블 구조 확인
DESCRIBE sb_rcm;
DESCRIBE sb_evaluation_sample;
DESCRIBE sb_design_evaluation_line;
DESCRIBE sb_design_evaluation_header;
```

### 2. 데이터 무결성 확인

```sql
-- 데이터 개수 확인
SELECT COUNT(*) FROM sb_rcm;
SELECT COUNT(*) FROM sb_evaluation_sample;

-- 백업과 비교 (백업 테이블이 있을 경우)
SELECT COUNT(*) FROM sb_evaluation_sample_backup;
```

### 3. 애플리케이션 테스트

- 웹 브라우저로 접속
- 설계평가 페이지 정상 작동 확인
- 운영평가 페이지 정상 작동 확인
- attribute 필드 입력/저장 확인

---

## 롤백 방법

### 방법 1: 백업에서 복원

```bash
# 애플리케이션 중지
sudo systemctl stop snowball

# 백업에서 복원
mysql -u사용자명 -p데이터베이스명 < backup_YYYYMMDD_HHMMSS.sql

# 애플리케이션 시작
sudo systemctl start snowball
```

### 방법 2: 개별 테이블 복원

```sql
-- sb_evaluation_sample 복원 (백업 테이블이 있을 경우)
DROP TABLE sb_evaluation_sample;
CREATE TABLE sb_evaluation_sample SELECT * FROM sb_evaluation_sample_backup;

-- user_id를 upload_user_id로 되돌림
ALTER TABLE sb_rcm CHANGE COLUMN user_id upload_user_id INT NOT NULL;
```

---

## 참고사항

### SQLite vs MySQL 차이점

| 항목 | SQLite (개발) | MySQL (운영) |
|------|---------------|--------------|
| 마이그레이션 | migrate.py 자동 실행 | 수동 SQL 실행 |
| 컬럼 삭제 | 테이블 재생성 필요 | ALTER TABLE DROP COLUMN |
| 트랜잭션 | 자동 | 명시적 COMMIT/ROLLBACK |
| TEXT 타입 | TEXT | TEXT/LONGTEXT |

### 향후 마이그레이션 관리

1. 개발환경에서 SQLite 마이그레이션 작성
2. MySQL 버전 SQL 스크립트 생성
3. 테스트 환경에서 먼저 실행
4. 운영환경에 적용

---

## 긴급 연락처

문제 발생 시:
- 개발팀: [연락처]
- DBA: [연락처]
