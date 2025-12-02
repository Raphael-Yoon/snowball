# 빠른 배포 가이드

## 🚀 MySQL에서 직접 실행 (가장 간단!)

---

## 1️⃣ 전체 재생성 (초기화)

```bash
mysql -u username -p < init_database.sql
```

**동작:**
- snowball DB 삭제 및 재생성
- 모든 테이블 생성 (19개)
- 뷰 생성 (1개)
- ✅ review_comment, design_comment 포함

**또는 MySQL 접속 후:**
```bash
mysql -u username -p
> source init_database.sql
> exit
```

---

## 2️⃣ 백업 → 복원

### 백업
```bash
mysqldump -u username -p snowball > backup.sql
```

### 복원
```bash
mysql -u username -p -e "CREATE DATABASE IF NOT EXISTS snowball CHARACTER SET utf8mb4"
mysql -u username -p snowball < backup.sql
```

---

## 3️⃣ 증분 업데이트 (변경사항만)

```bash
mysql -u username -p snowball < migrate_incremental.sql
```

**동작:**
- review_comment 컬럼 추가 (없으면)
- design_comment 컬럼 추가 (없으면)
- ✅ 기존 데이터 유지
- ✅ 중복 실행 안전

---

## 📊 언제 뭘 쓰나요?

| 상황 | 명령어 | 파일 |
|------|--------|------|
| **최초 배포** | `mysql < init_database.sql` | init_database.sql |
| **백업/복원** | `mysql < backup.sql` | backup.sql |
| **라이브 업데이트** | `mysql < migrate_incremental.sql` | migrate_incremental.sql |

---

## ✅ 현재 권장 (라이브 전)

### 방법 A: 로컬 DB → 운영 서버 복사

```bash
# === 로컬 ===
mysqldump -u root -p snowball > snowball.sql

# === 운영서버 ===
mysql -u username -p < snowball.sql
```

### 방법 B: SQL 스크립트로 초기화

```bash
# === 운영서버 ===
mysql -u username -p < init_database.sql

# 그 다음 초기 데이터 입력 (사용자, Lookup 등)
```

---

## 🔍 상태 확인

```bash
# 테이블 목록
mysql -u username -p snowball -e "SHOW TABLES;"

# 컬럼 확인
mysql -u username -p snowball -e "DESCRIBE sb_operation_evaluation_line;"

# 마이그레이션 히스토리
mysql -u username -p snowball -e "SELECT * FROM sb_migration_history;"
```

---

## ⚠️ 주의사항

### 초기화 (init_database.sql)
- ❌ 기존 snowball DB를 **완전히 삭제**합니다
- ⚠️ 운영 서버에서 실행 시 **반드시 백업** 먼저!
- ✅ 최초 배포 또는 개발 환경에서만 사용

### 증분 마이그레이션 (migrate_incremental.sql)
- ✅ 기존 데이터 유지
- ✅ 중복 실행 가능 (이미 적용된 것은 건너뜀)
- ✅ 라이브 운영 중에도 안전

---

## 📝 새 마이그레이션 추가 방법

`migrate_incremental.sql` 파일 끝에 추가:

```sql
-- ============================================================================
-- 마이그레이션 003: 새 컬럼 추가
-- ============================================================================

SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
    AND table_name = 'sb_operation_evaluation_line'
    AND column_name = 'approval_status'
);

SET @sql_003 = IF(@column_exists = 0,
    'ALTER TABLE sb_operation_evaluation_line ADD COLUMN approval_status VARCHAR(50) DEFAULT "pending"',
    'SELECT "Column already exists" AS status'
);

PREPARE stmt FROM @sql_003;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

INSERT IGNORE INTO sb_migration_history (version, name, status)
VALUES ('003', 'add_approval_status', 'success');
```

---

**자세한 내용**: [DB_COMMANDS.md](DB_COMMANDS.md) 참고
