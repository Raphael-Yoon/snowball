# Snowball 프로젝트

> RCM(Risk and Control Matrix) 관리 및 평가 시스템

## 📋 목차
- [개발 규칙](#개발-규칙)
- [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
- [시스템 구조](#시스템-구조)
- [최근 작업 내역](#최근-작업-내역)

---

## 개발 규칙

### ⚠️ 중요한 작업 지침

#### 서버 실행 금지
- **절대 `python snowball.py` 명령으로 서버를 실행하지 말 것**
- 백그라운드 프로세스도 실행하지 말 것
- 답변은 반드시 한국어로 할 것

#### 데이터베이스 작업 규칙

##### 🚫 절대 하지 말아야 할 것

1. **`auth.py`에 DDL 작성 금지**
   - ❌ `CREATE TABLE`
   - ❌ `ALTER TABLE`
   - ❌ `DROP TABLE`
   - ❌ `CREATE VIEW`
   - ❌ `DROP VIEW`

2. **서버 시작 시 스키마 변경 금지**
   - ❌ `init_db()` 같은 자동 실행 함수
   - ❌ `@app.before_first_request`에서 DDL 실행
   - ❌ 모듈 import 시 자동 실행되는 DDL

3. **코드에 하드코딩된 스키마 변경 금지**
   - ❌ 애플리케이션 코드에서 직접 `CREATE TABLE` 실행
   - ❌ 조건문으로 테이블 존재 여부 확인 후 생성

##### ✅ 올바른 방법: 마이그레이션 사용

모든 DDL은 `migrations/versions/` 디렉토리에 마이그레이션 파일로 작성:

```python
# migrations/versions/003_add_new_table.py
"""
새로운 테이블 추가
"""

def upgrade(conn):
    """스키마 업그레이드"""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sb_new_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    print("  테이블 생성 완료")

def downgrade(conn):
    """스키마 다운그레이드"""
    conn.execute('DROP TABLE IF EXISTS sb_new_table')
    print("  테이블 삭제 완료")
```

---

## 데이터베이스 마이그레이션

### 개요

모든 데이터베이스 스키마 변경은 마이그레이션 시스템을 통해 관리됩니다.

**마이그레이션 시스템의 장점:**
- ✅ **버전 관리**: 각 스키마 변경사항이 파일로 기록
- ✅ **추적 가능**: 어떤 마이그레이션이 적용되었는지 DB에 기록
- ✅ **롤백 가능**: 문제 발생 시 이전 버전으로 되돌리기 가능
- ✅ **안전성**: 이미 적용된 마이그레이션은 자동으로 건너뜀
- ✅ **독립 실행**: 서버와 독립적으로 DB 스키마 관리

### 기본 사용법

#### 1. 마이그레이션 상태 확인
```bash
python migrate.py status
```

#### 2. 마이그레이션 실행 (업그레이드)
```bash
# 모든 대기 중인 마이그레이션 적용
python migrate.py upgrade

# 특정 버전까지만 적용
python migrate.py upgrade --target 003
```

#### 3. 마이그레이션 롤백 (다운그레이드)
```bash
python migrate.py downgrade --target 001
```

⚠️ **주의**: 롤백 시 데이터 손실이 발생할 수 있습니다. 프로덕션 환경에서는 반드시 백업 후 실행하세요.

### 새로운 마이그레이션 파일 작성

#### 파일명 규칙
- 순차적 번호로 시작 (001, 002, 003, ...)
- 언더스코어(_)로 구분
- 설명적인 이름 사용

예: `003_add_audit_table.py`

#### 필수 함수
- `upgrade(conn)`: 스키마 업그레이드 로직
- `downgrade(conn)`: 스키마 다운그레이드(롤백) 로직

### 디렉토리 구조
```
snowball/
├── migrations/
│   ├── migration_manager.py      # 마이그레이션 관리 클래스
│   ├── README.md                  # 상세 문서
│   └── versions/                  # 마이그레이션 파일들
│       ├── 001_initial_schema.py
│       ├── 002_create_rcm_detail_view.py
│       └── ...
├── migrate.py                     # 마이그레이션 실행 스크립트
└── auth.py                        # DDL 코드 없음
```

### 프로덕션 환경 주의사항

1. ⚠️ **반드시 데이터베이스 백업**
   ```bash
   cp snowball.db snowball.db.backup_$(date +%Y%m%d)
   ```

2. ⚠️ **마이그레이션 테스트**
   ```bash
   python migrate.py upgrade --database test.db
   ```

3. ⚠️ **서버 중지 후 실행**
   - 마이그레이션 실행 중에는 서버를 중지
   - 스키마 변경 중 서버 실행 시 오류 발생 가능

4. ⚠️ **롤백 계획 수립**
   - 문제 발생 시 롤백 방법 미리 준비
   - 필요시 백업 DB로 복구

---

## 시스템 구조

### Blueprint 모듈 (snowball_link1-9)

#### 🌐 Public 서비스

**snowball_link1.py** - RCM 생성 및 이메일 발송
- AI 기반 RCM 엑셀 파일 생성
- 생성된 파일 이메일 발송
- 파일 다운로드 기능

**snowball_link2.py** - AI RCM 검토
- RCM 파일 업로드 및 AI 분석
- 통제 설계 검토 및 개선안 제시
- 대화형 AI 인터뷰 기능
- 분석 결과 리포트 생성

**snowball_link4.py** - 비디오/가이드 데이터
- 비디오 가이드 페이지
- 교육 자료 및 설명서 제공
- 사용법 안내 콘텐츠

**snowball_link9.py** - 고객지원
- Contact Us 페이지
- 서비스 가입 문의 처리
- 피드백 수집 및 관리
- 이메일 자동 발송 시스템

#### 🔒 Private 서비스 (로그인 필요)

**snowball_link5.py** - RCM 조회/관리
- 사용자 RCM 목록 조회
- RCM 상세 정보 보기
- RCM 검색 및 필터링
- 접근 권한 관리

**snowball_link6.py** - 설계평가
- 설계평가 세션 관리
- 통제별 설계 적절성 평가
- 평가 진행상황 추적
- 완료/미완료 상태 관리
- 엑셀 다운로드 기능

**snowball_link7.py** - 운영평가
- 운영평가 세션 관리
- 핵심통제 중심 운영 평가
- 설계평가 연계 워크플로우
- 평가 결과 저장 및 추적

**snowball_link8.py** - 내부평가
- 내부평가 메인 대시보드
- 순차적 워크플로우: RCM평가 → 설계평가 → 운영평가
- 평가 진행상황 시각화
- 단계별 가이드 제공

### 워크플로우 체계

1. **Public 서비스**: link1(RCM생성) → link2(AI검토) → link4(가이드) → link9(문의)
2. **Private 서비스**: link5(RCM관리) → link6(설계평가) → link7(운영평가) → link8(내부평가)

### 주요 특징

- **보안**: Private 서비스는 login_required 데코레이터로 접근 제한
- **연계성**: 설계평가 완료 후 운영평가 진행 가능
- **순차처리**: 내부평가에서 전체 프로세스 통합 관리
- **관리자 권한**: 모든 사용자 데이터 접근 및 관리 가능

---

## 현재 진행 중인 작업

### 🚀 다음 작업: Private 운영평가 기능 구현

**목표**: 설계평가와 유사한 운영평가 완료 기능 구현

**주요 작업 항목:**
1. 운영평가 완료/완료취소 기능
2. 운영평가 진행률 표시
3. 운영평가 결과 엑셀 다운로드
4. 운영평가 세션 관리 (삭제, 아카이브)

**참고할 구현:**
- 설계평가 시스템 (`snowball_link6.py`, `templates/user_design_evaluation_rcm.jsp`)
- 운영평가 기본 구조 (`snowball_link7.py`)

**설계 결정사항:**
- 운영평가 대상: 핵심통제 중 설계평가 결과가 'effective'(적정)인 통제만
- 설계평가 결과 변경 시 운영평가 자동 동기화 (부적정→적정 시 추가)
- Header 기반 세션 관리 (Line은 통제별 상세 데이터)

---

## 최근 작업 내역

### 운영평가 시스템 (2025-10-01)

**운영평가 대상 통제 필터링**
1. ✅ 설계평가는 핵심/비핵심 모두 대상
2. ✅ 설계평가 결과: 'effective'(적정) / 'partially_effective' / 'ineffective'
3. ✅ 운영평가 대상: 핵심통제 중 설계평가 결과가 'effective'(적정)인 통제만
4. ✅ 설계평가 결과 변경 시 운영평가 자동 동기화
   - 부적정→적정: 운영평가에 자동 추가
   - 핵심/비핵심 변경: 운영평가에 영향 없음

**핵심 파일:**
- `auth.py`: `get_key_rcm_details()` - 핵심통제+적정 필터링
- `snowball_link7.py`: 설계평가 결과 변경 시 자동 동기화
- `templates/user_operation_evaluation.jsp`: UI 표시

### 설계평가 시스템

**완료된 주요 기능:**
1. ✅ 상태 판단 로직: header completed_date 기반
2. ✅ 완료/완료취소 버튼 토글
3. ✅ 엑셀 다운로드 기능 (Template 시트 기반)
4. ✅ RCM 파일명 추적 기능
5. ✅ 관리자 권한 접근 제어

**핵심 함수:**
- `updateProgress()` - 헤더 completed_date 기반 상태 업데이트
- `completeEvaluation()` - 완료/완료취소 처리
- `updateEvaluationUI()` - 개별 평가 항목 UI 업데이트
- `openEvaluationModal()` - 평가 모달 열기

---

## 빠른 참조

### 마이그레이션 명령어
```bash
# 상태 확인
python migrate.py status

# 업그레이드
python migrate.py upgrade

# 롤백
python migrate.py downgrade --target 003

# 테스트 DB 사용
python migrate.py upgrade --database test.db
```

### 코드 리뷰 체크리스트
- [ ] `auth.py`에 DDL 코드가 없는가?
- [ ] 다른 `.py` 파일에 `CREATE`, `ALTER`, `DROP` 문이 없는가?
- [ ] `migrations/versions/` 디렉토리에 새 파일이 있는가?
- [ ] `upgrade()`와 `downgrade()` 함수가 모두 구현되었는가?

---

**기억하세요:**
- 📝 모든 DDL은 `migrations/versions/`에
- 🚫 `auth.py`와 다른 `.py` 파일에 DDL 금지
- ✅ `upgrade()`와 `downgrade()` 모두 구현
- 🧪 로컬에서 테스트 후 커밋
