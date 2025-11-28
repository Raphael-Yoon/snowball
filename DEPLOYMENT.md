# Snowball 운영서버 배포 가이드

## 목차
1. [사전 준비](#사전-준비)
2. [수동 배포 방법](#수동-배포-방법)
3. [자동 배포 스크립트 사용](#자동-배포-스크립트-사용)
4. [트러블슈팅](#트러블슈팅)
5. [롤백 방법](#롤백-방법)

---

## 사전 준비

### 1. 서버 접속 정보 확인
- SSH 접속 주소
- 사용자 계정 및 권한
- 애플리케이션 설치 경로

### 2. 필요한 권한
- 데이터베이스 파일 읽기/쓰기 권한
- 애플리케이션 재시작 권한

---

## 수동 배포 방법

### Step 1: 서버 접속
```bash
ssh user@your-server.com
cd /path/to/snowball
```

### Step 2: 데이터베이스 백업 (필수!)
```bash
# 백업 디렉토리 생성
mkdir -p backups

# 현재 데이터베이스 백업
cp snowball.db backups/snowball.db.backup_$(date +%Y%m%d_%H%M%S)

# 백업 확인
ls -lh backups/
```

### Step 3: 최신 코드 가져오기
```bash
# Git 저장소에서 최신 코드 pull
git pull origin main

# 또는 특정 브랜치
git pull origin production
```

### Step 4: Python 패키지 업데이트
```bash
pip install -r requirements.txt
```

### Step 5: 마이그레이션 상태 확인
```bash
python migrate.py status
```

출력 예시:
```
현재 마이그레이션 상태:
  ✓ 001_initial_schema
  ✓ 017_add_sample_attributes
  ⏳ 021_add_evaluation_type_to_sample (대기 중)
```

### Step 6: 마이그레이션 실행
```bash
python migrate.py upgrade
```

### Step 7: 애플리케이션 재시작

#### A. systemd 사용 시
```bash
sudo systemctl restart snowball
sudo systemctl status snowball
```

#### B. supervisor 사용 시
```bash
supervisorctl restart snowball
supervisorctl status snowball
```

#### C. 직접 실행 시
```bash
# 기존 프로세스 종료
pkill -f "python snowball.py"

# 새로 시작 (백그라운드)
nohup python snowball.py > logs/app.log 2>&1 &

# 프로세스 확인
ps aux | grep snowball
```

### Step 8: 배포 확인
```bash
# 로그 확인
tail -f logs/app.log

# 또는
journalctl -u snowball -f
```

웹 브라우저에서 접속하여 정상 동작 확인

---

## 자동 배포 스크립트 사용

### 1. 배포 스크립트 설정

`deploy.sh` 파일의 설정을 환경에 맞게 수정:

```bash
# 파일 편집
nano deploy.sh

# 수정할 부분:
DEPLOY_DIR="/path/to/snowball"  # 실제 경로로 변경
```

### 2. 실행 권한 부여
```bash
chmod +x deploy.sh
```

### 3. 배포 실행
```bash
./deploy.sh
```

### 4. 배포 스크립트 동작 과정
1. 최신 코드 가져오기 (git pull)
2. Python 패키지 업데이트
3. 데이터베이스 자동 백업
4. 마이그레이션 상태 확인
5. 마이그레이션 자동 실행
6. 애플리케이션 자동 재시작

---

## 마이그레이션 명령어 상세

### 상태 확인
```bash
python migrate.py status
```

### 모든 마이그레이션 적용
```bash
python migrate.py upgrade
```

### 특정 버전까지만 적용
```bash
python migrate.py upgrade --target 021
```

### 특정 버전으로 롤백
```bash
python migrate.py downgrade --target 017
```

### 다른 데이터베이스 파일 사용
```bash
python migrate.py upgrade --database /path/to/other.db
```

---

## 트러블슈팅

### 문제 1: 마이그레이션 실행 권한 없음
```bash
# 데이터베이스 파일 권한 확인
ls -l snowball.db

# 권한 부여 (필요시)
chmod 664 snowball.db
```

### 문제 2: 마이그레이션이 적용되지 않음
```bash
# 마이그레이션 테이블 확인
sqlite3 snowball.db "SELECT * FROM migration_history ORDER BY applied_at DESC LIMIT 5;"

# 강제로 특정 마이그레이션 재실행 (주의!)
# migration_history 테이블에서 해당 버전 삭제 후 다시 실행
```

### 문제 3: 마이그레이션 중 에러 발생
```bash
# 1. 백업에서 복원
cp backups/snowball.db.backup_YYYYMMDD_HHMMSS snowball.db

# 2. 로그 확인
cat logs/migration.log

# 3. 문제 해결 후 다시 실행
python migrate.py upgrade
```

### 문제 4: 애플리케이션이 재시작되지 않음
```bash
# 프로세스 확인
ps aux | grep snowball

# 강제 종료
pkill -9 -f "python snowball.py"

# 포트 사용 확인
netstat -tulpn | grep :5001

# 점유된 포트 프로세스 종료
lsof -ti:5001 | xargs kill -9
```

---

## 롤백 방법

### 방법 1: 백업 복원 (가장 안전)
```bash
# 1. 애플리케이션 중지
sudo systemctl stop snowball

# 2. 현재 DB 백업 (만약을 위해)
cp snowball.db snowball.db.failed_$(date +%Y%m%d_%H%M%S)

# 3. 백업 복원
cp backups/snowball.db.backup_YYYYMMDD_HHMMSS snowball.db

# 4. 애플리케이션 시작
sudo systemctl start snowball
```

### 방법 2: 마이그레이션 다운그레이드
```bash
# 특정 버전으로 롤백
python migrate.py downgrade --target 017

# 애플리케이션 재시작
sudo systemctl restart snowball
```

---

## 이번 배포에서 적용되는 마이그레이션

### Migration 026: simplify_evaluation_sample
- **내용**: `sb_evaluation_sample` 테이블 간소화 (불필요한 컬럼 제거)
- **영향**:
  - 테이블 DROP & 재생성
  - 제거: request_number, requester_name, requester_department, approver_name, approver_department, approval_date
  - 유지: sample_id, line_id, sample_number, evidence, has_exception, mitigation, evaluation_type
- **위험도**: 중간 (테이블 재생성, 백업 필수!)

### Migration 027: add_attributes_to_evaluation_sample
- **내용**: `sb_evaluation_sample` 테이블에 `attribute0-9` 컬럼 추가
- **영향**: 기존 데이터 유지, 새 컬럼만 추가
- **위험도**: 낮음 (안전)

### Migration 028: add_no_occurrence_to_design_evaluation
- **내용**: 설계평가 테이블에 no_occurrence 관련 필드 추가
- **영향**: 기존 데이터 유지, 새 컬럼만 추가
- **위험도**: 낮음 (안전)

---

## 마이그레이션 주의사항

⚠️ **Migration 017, 021 관련 주의사항:**
- Migration 017 (add_sample_attributes)과 021 (add_evaluation_type_to_sample)은 Migration 026에서 테이블을 DROP/재생성하면서 무효화됩니다.
- 실제 attribute 컬럼 추가는 Migration 027에서 이루어집니다.
- 이미 적용된 마이그레이션이므로 삭제하지 마세요!

마이그레이션 시퀀스:
```
017 → attribute0-9 추가
021 → evaluation_type 추가
026 → 테이블 DROP & 재생성 (attribute 컬럼 없이)
027 → attribute0-9 재추가 (최종 구현)
028 → no_occurrence 관련 필드 추가
```

---

## 배포 체크리스트

배포 전:
- [ ] 백업 확인
- [ ] 마이그레이션 테스트 (개발/스테이징 환경)
- [ ] 배포 시간 공지 (사용자에게)

배포 중:
- [ ] 코드 업데이트 완료
- [ ] 마이그레이션 성공
- [ ] 애플리케이션 재시작 완료

배포 후:
- [ ] 웹 접속 확인
- [ ] 주요 기능 테스트
- [ ] 로그 확인 (에러 없는지)
- [ ] 사용자 피드백 모니터링

---

## 긴급 연락처

문제 발생 시:
- 개발팀: [연락처]
- 시스템 관리자: [연락처]
- 에스컬레이션: [연락처]

---

## 참고 자료

- [마이그레이션 코드 위치](./migrations/versions/)
- [마이그레이션 관리자](./migrations/migration_manager.py)
- [데이터베이스 스키마](./migrations/versions/001_initial_schema.py)
