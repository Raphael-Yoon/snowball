# Claude Code 작업 메모

## 중요한 작업 지침

### 서버 실행 금지
- **절대 `python snowball.py` 명령으로 서버를 실행하지 말 것**
- 백그라운드 프로세스도 실행하지 말 것
- 답변은 반드시 한국어로 할 것

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

7. **RCM 파일명 추적 기능** (완료)
   - sb_rcm 테이블에 original_filename 컬럼 추가
   - create_rcm 함수에 파일명 파라미터 추가
   - 업로드 시 원본 파일명 저장
   - 관리자 화면에 파일명 표시

8. **관리자 권한 접근 문제 해결** (완료)
   - 모든 설계평가 API 엔드포인트에 관리자 권한 체크 추가
   - save, reset, complete, cancel, create-evaluation, delete-session, sessions, load API 수정
   - 관리자는 명시적 권한 없이도 모든 RCM 접근 가능

9. **다운로드 버튼 조건부 표시** (완료)
   - 다운로드 버튼이 완료 상태에서만 표시되도록 수정
   - updateProgress() 함수에서 다운로드 버튼 표시/숨김 제어 추가
   - 완료/완료취소 후 즉시 버튼 상태 업데이트

10. **엑셀 다운로드 기능 구현** (완료)
   - 원본 RCM 파일의 Template 시트를 통제별로 복사하여 엑셀 파일 생성
   - 각 통제 코드를 시트명으로 사용
   - C7~C11 셀에 통제번호, 통제명, 통제주기, 통제구분, 테스트 절차 자동 입력
   - 새로운 API 엔드포인트: /api/design-evaluation/download-excel/<rcm_id>
   - 프론트엔드 다운로드 함수 수정으로 엑셀 파일 다운로드

## 현재 상태
- 모든 주요 기능 구현 완료
- 완료취소 후 버튼 클릭 문제 해결됨
- RCM 파일명 추적 기능 추가
- 관리자 권한 접근 문제 해결됨
- 다운로드 버튼 조건부 표시 기능 추가
- 엑셀 다운로드 기능 구현 완료
- 디버깅 로그 추가되어 있음 (필요시 제거 가능)