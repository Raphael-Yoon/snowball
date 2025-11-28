#!/bin/bash
#
# Snowball 운영서버 배포 스크립트
# 사용법: ./deploy.sh
#

set -e  # 에러 발생 시 스크립트 중단

echo "====================================="
echo "Snowball 운영서버 배포 시작"
echo "====================================="

# 배포 디렉토리 (실제 환경에 맞게 수정)
DEPLOY_DIR="/path/to/snowball"
BACKUP_DIR="$DEPLOY_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

echo ""
echo "[1/6] 최신 코드 가져오기..."
cd $DEPLOY_DIR
git pull origin main

echo ""
echo "[2/6] Python 패키지 업데이트..."
pip install -r requirements.txt --quiet

echo ""
echo "[3/6] 데이터베이스 백업..."
if [ -f "snowball.db" ]; then
    cp snowball.db $BACKUP_DIR/snowball.db.backup_$TIMESTAMP
    echo "✓ 백업 완료: $BACKUP_DIR/snowball.db.backup_$TIMESTAMP"
else
    echo "⚠ snowball.db 파일을 찾을 수 없습니다."
fi

echo ""
echo "[4/6] 마이그레이션 상태 확인..."
python migrate.py status

echo ""
echo "[5/6] 데이터베이스 마이그레이션 실행..."
python migrate.py upgrade

echo ""
echo "[6/6] 애플리케이션 재시작..."
# 실행 방법에 맞게 수정하세요
# sudo systemctl restart snowball
# 또는
# supervisorctl restart snowball
# 또는
pkill -f "python snowball.py" && nohup python snowball.py > /dev/null 2>&1 &
echo "✓ 애플리케이션 재시작 완료"

echo ""
echo "====================================="
echo "배포 완료!"
echo "====================================="
echo ""
echo "백업 파일: $BACKUP_DIR/snowball.db.backup_$TIMESTAMP"
echo ""
