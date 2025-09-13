# Claude Code 작업 메모

## 중요한 작업 지침

### 서버 실행 금지
- **절대 `python snowball.py` 명령으로 서버를 실행하지 말 것**
- 백그라운드 프로세스도 실행하지 말 것
- 사용자가 여러 번 명시적으로 요청함

### 현재 진행 중인 작업: RCM 설계평가 시스템

#### 최근 완료된 주요 기능들:

1. **상태 판단 로직 변경** (완료)
   - 개별 통제 evaluation_date → header completed_date 기반으로 변경
   - 상태: "진행중", "완료" 두 가지만 표시

2. **완료/완료취소 버튼 토글** (완료)
   - 진행중 → "완료" 버튼 표시
   - 완료됨 → "완료취소" 버튼 표시
   - 헤더 completed_date 조정

3. **완료 처리 로직 정리** (완료)
   - 완료버튼 클릭시에만 completed_date 설정
   - 완료취소 버튼 클릭시에만 completed_date 삭제
   - 자동 완료 처리 로직 모두 제거

4. **평가 모달 저장 버튼 수정** (완료)
   - 버튼 ID 추가 및 다중 선택자 적용

5. **즉시 UI 업데이트** (완료)
   - 완료/완료취소 후 페이지 새로고침 없이 즉시 버튼 상태 변경

6. **완료취소 후 버튼 클릭 문제 수정** (완료)
   - openEvaluationModal 함수의 헤더 완료 상태 확인 로직 강화
   - sessionStorage 값 제거 로직 강화

#### 핵심 파일들:
- `templates/user_design_evaluation_rcm.jsp` - 메인 UI 로직
- `snowball_link6.py` - API 엔드포인트
- `auth.py` - 데이터베이스 업데이트 로직

#### 중요한 함수들:
- `updateProgress()` - 헤더 completed_date 기반 상태 업데이트
- `completeEvaluation()` - 완료/완료취소 처리
- `updateEvaluationUI()` - 개별 평가 항목 UI 업데이트
- `openEvaluationModal()` - 평가 모달 열기 (완료 상태 체크)

## 현재 상태
- 모든 주요 기능 구현 완료
- 완료취소 후 버튼 클릭 문제 해결됨
- 디버깅 로그 추가되어 있음 (필요시 제거 가능)