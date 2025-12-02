===============================================
운영평가 템플릿 파일 교체 안내
===============================================

## 현재 상황
운영평가 다운로드 기능의 엑셀 템플릿이 수정되었습니다.

## 수정 내용
- 12행(C12): 검토 결과(설계평가)
- 13행(C13): 검토 결과(운영평가 의견) [변경됨]
- 14행(C14): 결론(운영평가) [변경됨]

## 파일 교체 방법

1. 현재 열려있는 Template_Manual.xlsx 파일을 모두 닫아주세요
   (VSCode, Excel, 또는 다른 프로그램에서 열려있을 수 있습니다)

2. 아래 파일들을 확인하세요:
   - 기존 파일: c:\Pythons\snowball\paper_templates\Template_Manual.xlsx
   - 새 파일: c:\Pythons\snowball\paper_templates\Template_Manual_new.xlsx
   - 백업 파일: c:\Pythons\snowball\paper_templates\Template_Manual_backup.xlsx

3. 파일 교체:
   a) 기존 Template_Manual.xlsx 파일을 삭제하거나 이름을 변경
   b) Template_Manual_new.xlsx 파일의 이름을 Template_Manual.xlsx로 변경

4. 또는 아래 Python 스크립트를 실행:
   python c:\Pythons\snowball\replace_template.py

===============================================
