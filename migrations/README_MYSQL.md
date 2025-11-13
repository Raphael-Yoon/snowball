# MySQL 마이그레이션 가이드

운영 서버(PythonAnywhere)에서 SQLite 스키마를 MySQL로 마이그레이션하는 방법

## 1. 전체 스키마 동기화

로컬 SQLite의 모든 테이블을 MySQL로 복사 (데이터 제외)

```bash
cd /home/itap/snowball
python sync_sqlite_to_mysql.py          # Dry run (미리보기)
python sync_sqlite_to_mysql.py --apply  # 실제 적용
```

**주의**: 이 스크립트는 운영 서버에서만 실행하세요 (외부 접속 불가)

## 2. 뷰(View) 동기화

SQLite의 모든 뷰를 MySQL로 마이그레이션

```bash
cd /home/itap/snowball
python migrations/sync_views_to_mysql.py          # Dry run
python migrations/sync_views_to_mysql.py --apply  # 실제 적용
```

**현재 뷰 목록**:
- `sb_rcm_detail_v`: RCM 상세 정보 + lookup 테이블 조인

## 3. 수동으로 뷰 생성 (빠른 방법)

MySQL 콘솔에서 직접 실행:

```bash
cd /home/itap/snowball
mysql -u itap -p'qpspelrxm1!' itap\$snowball < migrations/create_mysql_view.sql
```

또는 MySQL 콘솔에서:

```sql
USE itap$snowball;

DROP VIEW IF EXISTS sb_rcm_detail_v;

CREATE VIEW sb_rcm_detail_v AS
SELECT
    d.detail_id,
    d.rcm_id,
    d.control_code,
    d.control_name,
    d.control_description,
    COALESCE(lk.lookup_name, d.key_control) AS key_control,
    COALESCE(lf.lookup_name, d.control_frequency) AS control_frequency,
    COALESCE(lt.lookup_name, d.control_type) AS control_type,
    COALESCE(ln.lookup_name, d.control_nature) AS control_nature,
    d.population,
    d.population_completeness_check,
    d.population_count,
    d.test_procedure,
    d.mapped_std_control_id,
    d.mapped_date,
    d.mapped_by,
    d.ai_review_status,
    d.ai_review_recommendation,
    d.ai_reviewed_date,
    d.ai_reviewed_by,
    d.mapping_status
FROM sb_rcm_detail d
LEFT JOIN sb_lookup lk ON lk.lookup_type = 'key_control'
    AND UPPER(lk.lookup_code) = UPPER(d.key_control)
LEFT JOIN sb_lookup lf ON lf.lookup_type = 'control_frequency'
    AND UPPER(lf.lookup_code) = UPPER(d.control_frequency)
LEFT JOIN sb_lookup lt ON lt.lookup_type = 'control_type'
    AND UPPER(lt.lookup_code) = UPPER(d.control_type)
LEFT JOIN sb_lookup ln ON ln.lookup_type = 'control_nature'
    AND UPPER(ln.lookup_code) = UPPER(d.control_nature);

-- 확인
SELECT COUNT(*) FROM sb_rcm_detail_v;
```

## 4. 환경 변수 설정

운영 서버의 `.env` 파일에서 다음 설정 확인:

```bash
# MySQL 사용 활성화
DB_TYPE=mysql

# 또는
USE_MYSQL=true

# MySQL 접속 정보
MYSQL_HOST=itap.mysql.pythonanywhere-services.com
MYSQL_USER=itap
MYSQL_PASSWORD=qpspelrxm1!
MYSQL_DATABASE=itap$snowball
MYSQL_PORT=3306
```

## 5. 마이그레이션 후 확인

```bash
# Python에서 확인
python -c "
from auth import get_db
conn = get_db()
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM sb_rcm_detail_v')
print('뷰 레코드 수:', cursor.fetchone()[0])
"

# MySQL 콘솔에서 확인
mysql -u itap -p'qpspelrxm1!' itap\$snowball -e "SELECT COUNT(*) FROM sb_rcm_detail_v"
```

## 6. 웹앱 재시작

PythonAnywhere 웹 탭에서 "Reload" 버튼 클릭

## 문제 해결

### "no such table: sb_rcm_detail_v" 오류
→ 뷰가 생성되지 않았습니다. 위의 3번 방법으로 수동 생성

### "Can't connect to MySQL server" 오류
→ 로컬에서 실행하려고 했습니다. 운영 서버에서 실행하세요

### pymysql 설치 오류
```bash
pip install pymysql
```

## 정기 동기화 (권장)

로컬에서 개발 후 운영 서버 배포 시:

1. 로컬에서 마이그레이션 실행: `python migrations/run_migrations.py`
2. GitHub에 푸시
3. 운영 서버에서 pull
4. 운영 서버에서 뷰 동기화: `python migrations/sync_views_to_mysql.py --apply`
5. 웹앱 재시작
