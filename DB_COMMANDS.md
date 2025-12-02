# 데이터베이스 명령어 정리

## 📋 목차
1. [전체 재생성 (초기화)](#1-전체-재생성-초기화)
2. [백업 및 복원](#2-백업-및-복원)
3. [증분 업데이트](#3-증분-업데이트)

---

## 1. 전체 재생성 (초기화)

### 방법 A: Python 초기화 스크립트 (권장)

```bash
# DB_CONFIG 설정 후 실행
python init_database_mysql.py
```

**동작:**
- 기존 테이블 전체 삭제
- 최신 스키마로 테이블 재생성
- 뷰 생성
- ⚠️ 모든 데이터 삭제됨

---

### 방법 B: MySQL 명령어로 직접 실행

#### Step 1: 데이터베이스 삭제 및 재생성
```bash
mysql -u username -p
```

```sql
-- 1. 기존 DB 삭제
DROP DATABASE IF EXISTS snowball;

-- 2. 새 DB 생성
CREATE DATABASE snowball
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 3. DB 선택
USE snowball;

-- 4. 사용자 권한 부여 (필요시)
GRANT ALL PRIVILEGES ON snowball.* TO 'username'@'%';
FLUSH PRIVILEGES;
```

#### Step 2: 테이블 생성
```bash
# SQL 파일이 있는 경우
mysql -u username -p snowball < schema.sql

# 또는 Python 스크립트 실행
python init_database_mysql.py
```

#### Step 3: 데이터 입력
```bash
# 백업 데이터가 있는 경우
mysql -u username -p snowball < data_backup.sql

# 또는 초기 데이터 스크립트 실행
mysql -u username -p snowball < initial_data.sql
```

---

## 2. 백업 및 복원

### 백업 (Dump)

#### 전체 백업 (구조 + 데이터)
```bash
mysqldump -u username -p snowball > snowball_full_backup.sql
```

#### 구조만 백업
```bash
mysqldump -u username -p --no-data snowball > snowball_schema.sql
```

#### 데이터만 백업
```bash
mysqldump -u username -p --no-create-info snowball > snowball_data.sql
```

#### 특정 테이블만 백업
```bash
mysqldump -u username -p snowball sb_user sb_rcm > snowball_partial.sql
```

#### 압축 백업
```bash
mysqldump -u username -p snowball | gzip > snowball_backup.sql.gz
```

---

### 복원 (Restore)

#### 전체 복원
```bash
# 1. DB 생성 (없는 경우)
mysql -u username -p -e "CREATE DATABASE IF NOT EXISTS snowball CHARACTER SET utf8mb4"

# 2. 데이터 복원
mysql -u username -p snowball < snowball_full_backup.sql
```

#### 압축 파일 복원
```bash
gunzip < snowball_backup.sql.gz | mysql -u username -p snowball
```

#### 특정 테이블만 복원
```bash
mysql -u username -p snowball < snowball_partial.sql
```

---

## 3. 증분 업데이트

### 방법 A: Python 마이그레이션 스크립트 (권장)

```bash
# 라이브 운영 중 변경사항 적용
python migrate_incremental_mysql.py
```

**동작:**
- 기존 데이터 유지
- 새 컬럼 추가
- 인덱스 생성 등
- ✅ 데이터 보존

---

### 방법 B: MySQL 명령어로 직접 실행

```bash
mysql -u username -p snowball
```

#### 컬럼 추가
```sql
ALTER TABLE sb_operation_evaluation_line
ADD COLUMN review_comment TEXT;
```

#### 컬럼 삭제
```sql
ALTER TABLE sb_operation_evaluation_line
DROP COLUMN old_column;
```

#### 컬럼 수정
```sql
ALTER TABLE sb_operation_evaluation_line
MODIFY COLUMN conclusion VARCHAR(100);
```

#### 인덱스 생성
```sql
CREATE INDEX idx_control_code
ON sb_operation_evaluation_line(control_code);
```

---

## 📊 명령어 비교표

| 작업 | 명령어 | 데이터 | 용도 |
|------|--------|--------|------|
| **전체 재생성** | `python init_database_mysql.py` | 삭제 | 최초 배포 |
| **백업** | `mysqldump -u user -p snowball > backup.sql` | 유지 | 안전 보관 |
| **복원** | `mysql -u user -p snowball < backup.sql` | 복구 | 백업 복원 |
| **증분 업데이트** | `python migrate_incremental_mysql.py` | 유지 | 라이브 업데이트 |

---

## 🎯 시나리오별 명령어

### 시나리오 1: 로컬 개발 DB → 운영 서버 최초 배포

```bash
# === 로컬에서 ===
# 1. 백업
mysqldump -u root -p snowball > snowball_export.sql

# 2. 압축 (선택)
gzip snowball_export.sql

# === 운영서버에서 ===
# 3. DB 생성
mysql -u username -p -e "CREATE DATABASE snowball CHARACTER SET utf8mb4"

# 4. 복원
mysql -u username -p snowball < snowball_export.sql

# 5. 확인
mysql -u username -p snowball -e "SHOW TABLES;"
```

---

### 시나리오 2: 운영 서버 DB 완전 초기화

```bash
# 1. 백업 (필수!)
mysqldump -u username -p snowball > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Python 스크립트로 초기화
python init_database_mysql.py

# 3. 확인
mysql -u username -p snowball -e "SHOW TABLES;"
```

---

### 시나리오 3: 라이브 운영 중 테이블 변경

```bash
# 1. 백업 (필수!)
mysqldump -u username -p snowball > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 서버 중지
# Flask 앱 종료

# 3. 마이그레이션 실행
python migrate_incremental_mysql.py

# 4. 서버 재시작
python snowball.py
```

---

### 시나리오 4: 문제 발생 시 백업 복원

```bash
# 1. 서버 중지

# 2. DB 삭제 및 재생성
mysql -u username -p -e "DROP DATABASE snowball"
mysql -u username -p -e "CREATE DATABASE snowball CHARACTER SET utf8mb4"

# 3. 백업 복원
mysql -u username -p snowball < backup_20251202_150000.sql

# 4. 서버 재시작
python snowball.py
```

---

## 🔍 상태 확인 명령어

### 테이블 목록 확인
```bash
mysql -u username -p snowball -e "SHOW TABLES;"
```

### 테이블 구조 확인
```bash
mysql -u username -p snowball -e "DESCRIBE sb_operation_evaluation_line;"
```

### 특정 컬럼 존재 확인
```bash
mysql -u username -p snowball -e "SHOW COLUMNS FROM sb_operation_evaluation_line LIKE 'review_comment';"
```

### 마이그레이션 히스토리 확인
```bash
mysql -u username -p snowball -e "SELECT * FROM sb_migration_history ORDER BY version;"
```

### 데이터 개수 확인
```bash
mysql -u username -p snowball -e "
SELECT
    'sb_user' as table_name, COUNT(*) as count FROM sb_user
UNION ALL
SELECT 'sb_rcm', COUNT(*) FROM sb_rcm
UNION ALL
SELECT 'sb_design_evaluation_line', COUNT(*) FROM sb_design_evaluation_line
UNION ALL
SELECT 'sb_operation_evaluation_line', COUNT(*) FROM sb_operation_evaluation_line;
"
```

---

## 💡 유용한 팁

### 1. 백업 자동화
```bash
# cron job으로 매일 백업
0 2 * * * mysqldump -u username -p'password' snowball > /backups/snowball_$(date +\%Y\%m\%d).sql
```

### 2. 원격 서버 백업
```bash
# 로컬에서 원격 서버 백업
mysqldump -h remote_host -u username -p snowball > remote_backup.sql
```

### 3. 특정 테이블 삭제 후 재생성
```bash
mysql -u username -p snowball -e "DROP TABLE IF EXISTS sb_temp_table;"
mysql -u username -p snowball < create_temp_table.sql
```

### 4. SQL 파일 직접 실행
```bash
mysql -u username -p snowball < migration_001.sql
```

---

## ⚠️ 주의사항

### 백업 관련
- ✅ 항상 작업 전 백업!
- ✅ 백업 파일은 여러 개 보관
- ✅ 복원 테스트 주기적으로 수행

### 데이터 삭제
- ❌ 운영 DB에서 DROP DATABASE 절대 주의!
- ❌ 백업 없이 초기화 금지!
- ⚠️ 삭제 명령어 실행 전 DB 이름 재확인

### 권한 문제
- `GRANT ALL PRIVILEGES` 신중히 사용
- 운영 환경에서는 최소 권한 원칙 적용
- 백업용 계정은 읽기 전용으로

---

## 📞 문제 해결

### Q: "Access denied" 오류
```bash
# 권한 확인
mysql -u root -p -e "SHOW GRANTS FOR 'username'@'%';"

# 권한 부여
mysql -u root -p -e "GRANT ALL PRIVILEGES ON snowball.* TO 'username'@'%';"
mysql -u root -p -e "FLUSH PRIVILEGES;"
```

### Q: "Unknown database" 오류
```bash
# DB 생성
mysql -u username -p -e "CREATE DATABASE snowball CHARACTER SET utf8mb4;"
```

### Q: 복원 시 오류 발생
```bash
# 기존 DB 완전 삭제 후 재시도
mysql -u username -p -e "DROP DATABASE IF EXISTS snowball;"
mysql -u username -p -e "CREATE DATABASE snowball CHARACTER SET utf8mb4;"
mysql -u username -p snowball < backup.sql
```

---

**작성일**: 2025-12-02
**버전**: 1.0.0
