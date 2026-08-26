# 스노우볼 시스템 기술 명세 (Technical Specs)

> [!IMPORTANT]
> 에이전트 페르소나, 직급 체계 및 전사 운영 규칙은 루트의 [CLAUDE.md](file:///CLAUDE.md) 및 [.agents/AGENT.md](file:///.agents/AGENT.md)를 준수한다. 본 파일은 프로젝트별 기술 명령어 및 파일 참조용으로만 활용한다.

## 1. 빌드 및 실행 명령어 (Build & Run)

- **메인 애플리케이션 실행**: `python snowball.py`
- **데이터베이스 마이그레이션**: `flask db upgrade`
- **구글 드라이브 동기화 및 작업로그**: `python snowball_drive.py`

## 2. 작업 로그 관리 (담당: 유재욱)

- 사용자가 "작업 내용 기록해", "작업 로그 작성해줘" 등을 요청할 경우 **[유재욱]**이 담당한다.
- `WORK_LOG.md` 양식을 준수하여 Google Docs(`work_log`)에 최신순으로 기록한다.

## 3. 프로젝트 파일 참조 (Reference)

| 파일 | 설명 |
|------|------|
| `snowball.py` | 메인 애플리케이션 |
| `snowball_link1~11.py` | 기능별 모듈 (링크 처리) |
| `snowball_drive.py` | Google Drive 연동 및 작업 로그 |
| `snowball_mail.py` | 메일 발송 모듈 |
| `snowball_admin.py` | 관리자 기능 |
| `db_config.py` | DB 설정 |
| `auth.py` | 인증 모듈 |
| `evaluation_utils.py` | 평가 유틸리티 |
| `snowball.db` | SQLite 메인 데이터베이스 |
| `WORK_LOG.md` | 작업 로그 관리 지침 |

## 4. 환경 관리 원칙 (Local)

- **보존 대상**: `snowball.db`, `logs/`, `migrations/`, `paper_templates/`, `progress_data/`
- **삭제 대상**: 작업 중 생성한 임시 `.py` 스크립트 및 테스트 결과물
