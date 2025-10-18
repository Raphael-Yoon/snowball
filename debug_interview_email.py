#!/usr/bin/env python3
"""
인터뷰 이메일 전송 디버그 스크립트
실제로 메일이 전송되는지 확인합니다.
"""

import sys
import os

# snowball 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from snowball_link2 import export_interview_excel_and_send, get_text_itgc, fill_sheet, is_ineffective, question_count
from snowball_mail import send_gmail_with_attachment

def test_interview_email():
    """인터뷰 이메일 전송 테스트"""

    print("=" * 60)
    print("인터뷰 이메일 전송 디버그 테스트")
    print("=" * 60)

    # 테스트 데이터 준비
    test_email = input("\n테스트 메일을 받을 이메일 주소를 입력하세요: ").strip()

    if not test_email:
        print("❌ 이메일 주소가 입력되지 않았습니다.")
        return

    print(f"\n📧 테스트 이메일 주소: {test_email}")
    print("\n간단한 테스트 답변으로 인터뷰 이메일을 생성합니다...")

    # 간단한 답변 데이터 생성
    answers = [test_email, 'TestSystem'] + ['테스트 답변'] * (question_count - 2)
    textarea_answers = [''] * question_count

    print(f"✅ 답변 데이터 준비 완료 (총 {question_count}개 질문)")

    # 진행 상황 출력 함수
    def progress_callback(percentage, message):
        print(f"  [{percentage}%] {message}")

    print("\n🚀 이메일 생성 및 전송 시작...")
    print("-" * 60)

    try:
        # 이메일 생성 및 전송 실행
        success, returned_email, error = export_interview_excel_and_send(
            answers=answers,
            textarea_answers=textarea_answers,
            get_text_itgc=get_text_itgc,
            fill_sheet=fill_sheet,
            is_ineffective=is_ineffective,
            send_gmail_with_attachment=send_gmail_with_attachment,
            enable_ai_review=False,  # AI 검토 비활성화 (빠른 테스트)
            progress_callback=progress_callback
        )

        print("-" * 60)

        if success:
            print(f"\n✅ 성공! 이메일이 {returned_email}로 전송되었습니다!")
            print("\n📮 메일함을 확인해주세요.")
            print("   - 받은편지함")
            print("   - 스팸함도 확인")
            print(f"   - BCC로 snowball2727@naver.com에도 전송됨")
        else:
            print(f"\n❌ 실패! 에러: {error}")
            print("\n가능한 원인:")
            print("   1. Gmail API 인증 문제 (token.pickle, credentials.json)")
            print("   2. OpenAI API 키 문제 (enable_ai_review=True인 경우)")
            print("   3. Excel 파일 생성 문제")
            print("   4. 네트워크 연결 문제")

    except Exception as e:
        print(f"\n💥 예외 발생: {e}")
        import traceback
        print("\n상세 에러:")
        traceback.print_exc()

if __name__ == '__main__':
    test_interview_email()
