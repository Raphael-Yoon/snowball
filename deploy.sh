#!/bin/bash
# 운영 서버 배포 스크립트

echo "📦 배포 시작..."

# 최신 코드 받기
git pull origin master

# 운영에 불필요한 폴더/파일 삭제
echo "🧹 불필요한 파일 정리 중..."

# 테스트 및 개발용
rm -rf test/
rm -rf __pycache__/
rm -rf .claude/
rm -rf .vscode/
rm -rf migrations/
rm -f migrate.py
rm -f cleanup_test_data.py
rm -f list_tables.py
rm -f WORK_LOG.md
rm -f current_questions.txt
rm -f Pythons.code-workspace

# 캐시 파일
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# 임시 폴더 비우기 (폴더는 유지)
rm -rf temp/*
rm -rf downloads/*

echo "✅ 배포 완료!"
echo "   - test/, .claude/, .vscode/ 등 개발용 폴더 제거됨"
echo "   - 캐시 파일 정리됨"
