from auth import get_db

def cleanup():
    with get_db() as conn:
        # 1. 테스트용 RCM 찾기 (Design_Test_RCM_...)
        rcms = conn.execute("SELECT rcm_id, rcm_name FROM sb_rcm WHERE rcm_name LIKE 'Design_Test_RCM_%'").fetchall()
        if not rcms:
            print("삭제할 테스트 RCM이 없습니다.")
            return

        for rcm in rcms:
            rcm_id = rcm['rcm_id']
            rcm_name = rcm['rcm_name']
            print(f"정리 중: {rcm_name} (ID: {rcm_id})")

            # 해당 RCM의 헤더 찾기
            headers = conn.execute("SELECT header_id FROM sb_evaluation_header WHERE rcm_id = ?", (rcm_id,)).fetchall()
            for header in headers:
                h_id = header['header_id']
                # 평가 라인 삭제
                lines = conn.execute("SELECT line_id FROM sb_evaluation_line WHERE header_id = ?", (h_id,)).fetchall()
                for line in lines:
                    l_id = line['line_id']
                    # 샘플 삭제
                    conn.execute("DELETE FROM sb_evaluation_sample WHERE line_id = ?", (l_id,))
                    # 이미지 삭제
                    conn.execute("DELETE FROM sb_evaluation_image WHERE line_id = ?", (l_id,))
                
                conn.execute("DELETE FROM sb_evaluation_line WHERE header_id = ?", (h_id,))
                conn.execute("DELETE FROM sb_evaluation_header WHERE header_id = ?", (h_id,))
                print(f"  - 평가 세션 (ID: {h_id}) 관련 데이터 삭제 완료")

            # 유저 매핑 삭제
            conn.execute("DELETE FROM sb_user_rcm WHERE rcm_id = ?", (rcm_id,))
            # RCM 상세 삭제
            conn.execute("DELETE FROM sb_rcm_detail WHERE rcm_id = ?", (rcm_id,))
            # RCM 자체 삭제
            conn.execute("DELETE FROM sb_rcm WHERE rcm_id = ?", (rcm_id,))
            print(f"  - RCM {rcm_name} 및 관련 매핑/상세 정보 삭제 완료")
        
        conn.commit()
        print("\n[성공] 모든 테스트용 임시 데이터가 정리되었습니다.")

if __name__ == '__main__':
    cleanup()
