# 빠른 배포 가이드

## 🚀 3가지 명령어만 기억하세요

---

## 1️⃣ 전체 재생성 (모든 테이블 + 데이터 새로 만들기)

### Python 스크립트 (추천)
```bash
python init_database_mysql.py
```
- 모든 테이블 삭제 → 재생성
- ⚠️ 모든 데이터 삭제됨

### 직접 명령어
```bash
# 1. DB 삭제 및 재생성
mysql -u username -p -e "DROP DATABASE IF EXISTS snowball; CREATE DATABASE snowball CHARACTER SET utf8mb4;"

# 2. 테이블 생성
python init_database_mysql.py

# 또는 SQL 파일 있으면
mysql -u username -p snowball < schema.sql
```

---

## 2️⃣ 백업 → 복원 (DB 통째로 복사)

### 백업
```bash
mysqldump -u username -p snowball > backup.sql
```

### 복원
```bash
# 1. DB 생성 (필요시)
mysql -u username -p -e "CREATE DATABASE IF NOT EXISTS snowball CHARACTER SET utf8mb4"

# 2. 복원
mysql -u username -p snowball < backup.sql
```

---

## 3️⃣ 증분 업데이트 (변경사항만 적용)

```bash
python migrate_incremental_mysql.py
```
- 컬럼 추가 등
- ✅ 기존 데이터 유지

---

## 📊 언제 뭘 쓰나요?

| 상황 | 명령어 |
|------|--------|
| **최초 배포** | `mysqldump` → `mysql < backup.sql` |
| **개발 DB 초기화** | `python init_database_mysql.py` |
| **라이브 업데이트** | `python migrate_incremental_mysql.py` |
| **문제 발생 복구** | `mysql < backup.sql` |

---

## ✅ 현재 상황 (라이브 전): 백업 → 복원

```bash
# === 로컬 ===
mysqldump -u root -p snowball > snowball.sql

# === 운영서버 ===
mysql -u username -p -e "CREATE DATABASE snowball CHARACTER SET utf8mb4"
mysql -u username -p snowball < snowball.sql
python snowball.py
```

**끝!** 🎉

---

## 🔍 상태 확인

```bash
# 테이블 목록
mysql -u username -p snowball -e "SHOW TABLES;"

# 마이그레이션 히스토리
mysql -u username -p snowball -e "SELECT * FROM sb_migration_history;"
```

---

**자세한 내용**: [DB_COMMANDS.md](DB_COMMANDS.md) 참고
