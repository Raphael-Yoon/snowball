#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MySQL 연결 상태 확인 스크립트"""

import subprocess
import socket

print("=" * 70)
print("MySQL 연결 진단")
print("=" * 70)
print()

# 1. MySQL 서버 프로세스 확인
print("[1] MySQL 서버 프로세스 확인")
try:
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    mysql_processes = [line for line in result.stdout.split('\n') if 'mysql' in line.lower()]

    if mysql_processes:
        print("✅ MySQL 프로세스 실행 중:")
        for proc in mysql_processes[:3]:  # 처음 3개만 표시
            print(f"   {proc}")
    else:
        print("❌ MySQL 프로세스가 실행되지 않음")
        print()
        print("해결 방법:")
        print("  sudo systemctl start mysql")
        print("  # 또는")
        print("  sudo service mysql start")
except Exception as e:
    print(f"⚠️  확인 실패: {e}")

print()

# 2. MySQL 포트 확인
print("[2] MySQL 포트 3306 확인")
try:
    result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
    mysql_port = [line for line in result.stdout.split('\n') if '3306' in line]

    if mysql_port:
        print("✅ MySQL 포트 3306 리스닝 중:")
        for port in mysql_port:
            print(f"   {port}")
    else:
        print("❌ MySQL 포트 3306이 열려있지 않음")
        print()
        print("확인 사항:")
        print("  - MySQL 서버가 실행 중인가?")
        print("  - 다른 포트를 사용하는가?")
except Exception as e:
    print(f"⚠️  확인 실패: {e}")
    print("   대체 명령어: sudo lsof -i :3306")

print()

# 3. localhost 연결 테스트
print("[3] localhost:3306 연결 테스트")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('localhost', 3306))
    sock.close()

    if result == 0:
        print("✅ localhost:3306 연결 가능")
    else:
        print("❌ localhost:3306 연결 불가")
        print()
        print("원인:")
        print("  - MySQL 서버가 중지되어 있음")
        print("  - MySQL이 다른 포트에서 실행 중")
        print("  - MySQL이 unix socket만 사용 중")
except Exception as e:
    print(f"❌ 연결 실패: {e}")

print()

# 4. MySQL 상태 확인
print("[4] MySQL 서비스 상태")
try:
    result = subprocess.run(['systemctl', 'status', 'mysql'], capture_output=True, text=True)
    status_lines = result.stdout.split('\n')[:5]  # 처음 5줄만

    for line in status_lines:
        print(f"   {line}")

    if 'active (running)' in result.stdout:
        print()
        print("✅ MySQL 서비스 실행 중")
    elif 'inactive' in result.stdout or 'dead' in result.stdout:
        print()
        print("❌ MySQL 서비스 중지됨")
        print()
        print("시작 방법:")
        print("  sudo systemctl start mysql")
except Exception as e:
    print(f"⚠️  systemctl 명령 실패: {e}")
    print()
    print("대체 명령어 시도:")
    try:
        result = subprocess.run(['service', 'mysql', 'status'], capture_output=True, text=True)
        print(result.stdout[:200])
    except:
        print("  sudo service mysql status")

print()
print("=" * 70)
print("진단 완료")
print("=" * 70)
print()
print("다음 단계:")
print("1. MySQL 서버가 중지되어 있다면:")
print("   sudo systemctl start mysql")
print()
print("2. MySQL이 Unix socket만 사용한다면:")
print("   init_database_mysql.py의 DB_CONFIG에서")
print("   'host': 'localhost' → 'unix_socket': '/var/run/mysqld/mysqld.sock' 추가")
print()
print("3. MySQL이 다른 호스트에 있다면:")
print("   DB_CONFIG의 'host' 값을 실제 호스트로 변경")
print()
