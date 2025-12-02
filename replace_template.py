#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Template_Manual.xlsx 파일 교체 스크립트"""

import os
import shutil
import time

template_path = r'c:\Pythons\snowball\paper_templates\Template_Manual.xlsx'
new_template_path = r'c:\Pythons\snowball\paper_templates\Template_Manual_new.xlsx'
backup_path = r'c:\Pythons\snowball\paper_templates\Template_Manual_old.xlsx'

print('템플릿 파일 교체를 시작합니다...\n')

# 새 파일 확인
if not os.path.exists(new_template_path):
    print(f'[ERROR] 새 템플릿 파일이 없습니다: {new_template_path}')
    print('먼저 update_template.py를 실행해주세요.')
    exit(1)

# 기존 파일 교체 시도
max_attempts = 5
for attempt in range(1, max_attempts + 1):
    try:
        print(f'[시도 {attempt}/{max_attempts}] 파일 교체 중...')

        # 기존 파일을 백업으로 이동
        if os.path.exists(template_path):
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.move(template_path, backup_path)
            print(f'  - 기존 파일을 백업으로 이동: {backup_path}')

        # 새 파일을 원래 이름으로 이동
        shutil.move(new_template_path, template_path)
        print(f'  - 새 파일로 교체 완료: {template_path}')
        print('\n[SUCCESS] 템플릿 파일 교체가 완료되었습니다!')
        break

    except PermissionError:
        if attempt < max_attempts:
            print(f'  - 파일이 사용 중입니다. {2}초 후 재시도...')
            time.sleep(2)
        else:
            print('\n[ERROR] 파일 교체에 실패했습니다.')
            print('다음 사항을 확인해주세요:')
            print('  1. Template_Manual.xlsx 파일이 Excel이나 다른 프로그램에서 열려있지 않은지')
            print('  2. VSCode에서 해당 파일을 닫았는지')
            print('  3. 파일 탐색기에서 해당 폴더를 열어놓지 않았는지')
            print(f'\n수동 교체 방법:')
            print(f'  1. {template_path} 파일을 삭제')
            print(f'  2. {new_template_path} 파일의 이름을 Template_Manual.xlsx로 변경')
            exit(1)
    except Exception as e:
        print(f'\n[ERROR] 예상치 못한 오류: {e}')
        exit(1)
