#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
질문 순서를 재정렬하는 스크립트
- 10번과 11번 질문을 23번 뒤로 이동 (22, 23번으로)
- 기존 12~23번 질문들을 10~21번으로 이동
"""

import re
import sys

def fix_question_order(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 질문 패턴을 찾아서 수정
        def replace_index(match):
            full_match = match.group(0)
            index = int(match.group(1))
            
            # 10번 -> 22번
            if index == 10:
                return full_match.replace(f'"index": {index}', f'"index": {22}')
            # 11번 -> 23번
            elif index == 11:
                return full_match.replace(f'"index": {index}', f'"index": {23}')
            # 12번부터 23번까지는 2씩 앞으로 이동
            elif index >= 12 and index <= 23:
                return full_match.replace(f'"index": {index}', f'"index": {index - 2}')
            
            return full_match
        
        # 질문 인덱스 패턴 찾아서 교체
        pattern = r'{"index": (\d+),[^}]+}'
        updated_content = re.sub(pattern, replace_index, content, flags=re.MULTILINE | re.DOTALL)
        
        # 파일에 쓰기
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        print("질문 순서가 성공적으로 수정되었습니다.")
        return True
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python fix_question_order.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    fix_question_order(file_path)