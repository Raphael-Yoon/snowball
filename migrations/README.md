# Snowball 데이터베이스 마이그레이션

## 개요
이 디렉토리는 Snowball 애플리케이션의 데이터베이스 스키마 변경사항을 관리합니다.

## 구조
```
migrations/
├── migration_manager.py  # 마이그레이션 관리 클래스
├── versions/             # 마이그레이션 파일들
│   ├── 001_initial_schema.py
│   ├── 002_add_lookup_table.py
│   └── ...
```

## 마이그레이션 파일 작성 규칙

각 마이그레이션 파일은 다음 구조를 따라야 합니다:

```python
"""
마이그레이션 설명
"""

def upgrade(conn):
    """스키마 업그레이드 로직"""
    pass

def downgrade(conn):
    """스키마 다운그레이드 로직 (롤백)"""
    pass
```

## 사용법

### 마이그레이션 실행
```bash
python migrate.py upgrade
```

### 특정 버전으로 마이그레이션
```bash
python migrate.py upgrade --target 003
```

### 마이그레이션 롤백
```bash
python migrate.py downgrade --target 002
```

### 마이그레이션 상태 확인
```bash
python migrate.py status
```

## 새 마이그레이션 생성

1. `versions/` 디렉토리에 새 파일 생성 (예: `004_add_new_table.py`)
2. `upgrade()`와 `downgrade()` 함수 구현
3. `python migrate.py upgrade` 실행

## 주의사항

- 마이그레이션 파일은 순차적 번호로 시작해야 함 (001, 002, 003...)
- 이미 실행된 마이그레이션은 자동으로 건너뜀
- 롤백 시 데이터 손실 가능성 주의
- 프로덕션 환경에서는 백업 후 실행 권장
