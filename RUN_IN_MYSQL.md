# MySQL에서 실행하는 명령어

## 🎯 2가지 방법

---

## 방법 1: MySQL 밖에서 실행 (추천)

### 전체 초기화
```bash
mysql -u username -p < init_database.sql
```

### 증분 마이그레이션
```bash
mysql -u username -p snowball < migrate_incremental.sql
```

**장점:**
- 가장 간단
- 한 줄로 끝
- 비밀번호 입력 후 자동 실행

---

## 방법 2: MySQL 안에서 실행

### Step 1: MySQL 접속
```bash
mysql -u username -p
```

비밀번호 입력

### Step 2: SQL 파일 실행

#### 전체 초기화
```sql
source /home/itap/snowball/init_database.sql;
```

또는

```sql
\. /home/itap/snowball/init_database.sql
```

#### 증분 마이그레이션
```sql
USE snowball;
source /home/itap/snowball/migrate_incremental.sql;
```

### Step 3: 확인
```sql
SHOW TABLES;
```

### Step 4: 종료
```sql
exit;
```

---

## 📋 전체 명령어 예시

### 시나리오: 운영서버 최초 배포

```bash
# 1. MySQL 접속
mysql -u username -p

# 비밀번호 입력 후...

# 2. SQL 파일 실행
mysql> source /home/itap/snowball/init_database.sql;

# 3. 결과 확인
mysql> SHOW TABLES;

# 4. 테이블 개수 확인 (19개여야 함)
mysql> SELECT COUNT(*) FROM information_schema.tables
       WHERE table_schema = 'snowball';

# 5. 마이그레이션 히스토리 확인
mysql> SELECT * FROM sb_migration_history;

# 6. 종료
mysql> exit;
```

---

### 시나리오: 증분 마이그레이션 (라이브 후)

```bash
# 1. 백업
mysqldump -u username -p snowball > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. MySQL 접속
mysql -u username -p

# 3. DB 선택
mysql> USE snowball;

# 4. 마이그레이션 실행
mysql> source /home/itap/snowball/migrate_incremental.sql;

# 5. 결과 확인
mysql> SELECT * FROM sb_migration_history ORDER BY version;

# 6. 컬럼 확인
mysql> DESCRIBE sb_operation_evaluation_line;
mysql> DESCRIBE sb_design_evaluation_line;

# 7. 종료
mysql> exit;
```

---

## 🔍 유용한 명령어

### 현재 DB 확인
```sql
SELECT DATABASE();
```

### DB 선택
```sql
USE snowball;
```

### 테이블 목록
```sql
SHOW TABLES;
```

### 테이블 구조 확인
```sql
DESCRIBE sb_operation_evaluation_line;
```

### 특정 컬럼 존재 확인
```sql
SHOW COLUMNS FROM sb_operation_evaluation_line LIKE 'review_comment';
```

### 데이터 확인
```sql
SELECT COUNT(*) FROM sb_user;
SELECT COUNT(*) FROM sb_rcm;
```

### 마이그레이션 히스토리
```sql
SELECT version, name, applied_at, status
FROM sb_migration_history
ORDER BY version;
```

---

## ⚠️ 주의사항

### source 명령어 사용 시
- ✅ 절대 경로 사용 권장: `/home/itap/snowball/init_database.sql`
- ✅ 상대 경로도 가능: `./init_database.sql` (현재 디렉토리 기준)
- ❌ Windows 경로는 슬래시 사용: `C:/Users/...` (백슬래시 X)

### 권한 문제
```sql
-- 권한 확인
SHOW GRANTS;

-- 권한이 없다면 root로 실행
mysql -u root -p < init_database.sql
```

---

## 💡 팁

### 실행 시간이 오래 걸리면
```sql
-- 진행 상황 확인 (다른 터미널에서)
mysql -u username -p -e "SHOW PROCESSLIST;"
```

### 오류 발생 시
```sql
-- 오류 메시지 자세히 보기
SHOW ERRORS;
SHOW WARNINGS;
```

### 특정 부분만 실행하고 싶다면
SQL 파일을 열어서 필요한 부분만 복사해서 실행

---

## 📝 요약

| 목적 | 명령어 |
|------|--------|
| **전체 초기화** | `mysql -u username -p < init_database.sql` |
| **증분 마이그레이션** | `mysql -u username -p snowball < migrate_incremental.sql` |
| **MySQL 내부** | `source /path/to/file.sql;` |
| **테이블 확인** | `SHOW TABLES;` |
| **컬럼 확인** | `DESCRIBE table_name;` |

---

**가장 간단한 방법:**
```bash
cd /home/itap/snowball
mysql -u username -p < init_database.sql
```

끝! 🎉
