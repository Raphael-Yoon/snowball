-- MySQL용 sb_rcm_detail_v 뷰 생성
-- PythonAnywhere MySQL 콘솔에서 실행하거나
-- mysql -u itap -p itap$snowball < create_mysql_view.sql

-- 기존 뷰 삭제 (있다면)
DROP VIEW IF EXISTS sb_rcm_detail_v;

-- sb_rcm_detail_v 뷰 생성
-- sb_lookup 테이블과 조인하여 코드값을 실제 이름으로 변환
CREATE VIEW sb_rcm_detail_v AS
SELECT
    d.detail_id,
    d.rcm_id,
    d.control_code,
    d.control_name,
    d.control_description,
    COALESCE(lk.lookup_name, d.key_control) AS key_control,
    COALESCE(lf.lookup_name, d.control_frequency) AS control_frequency,
    COALESCE(lt.lookup_name, d.control_type) AS control_type,
    COALESCE(ln.lookup_name, d.control_nature) AS control_nature,
    d.population,
    d.population_completeness_check,
    d.population_count,
    d.test_procedure,
    d.mapped_std_control_id,
    d.mapped_date,
    d.mapped_by,
    d.ai_review_status,
    d.ai_review_recommendation,
    d.ai_reviewed_date,
    d.ai_reviewed_by,
    d.mapping_status
FROM sb_rcm_detail d
LEFT JOIN sb_lookup lk ON lk.lookup_type = 'key_control'
    AND UPPER(lk.lookup_code) = UPPER(d.key_control)
LEFT JOIN sb_lookup lf ON lf.lookup_type = 'control_frequency'
    AND UPPER(lf.lookup_code) = UPPER(d.control_frequency)
LEFT JOIN sb_lookup lt ON lt.lookup_type = 'control_type'
    AND UPPER(lt.lookup_code) = UPPER(d.control_type)
LEFT JOIN sb_lookup ln ON ln.lookup_type = 'control_nature'
    AND UPPER(ln.lookup_code) = UPPER(d.control_nature);

-- 뷰 생성 확인
SELECT COUNT(*) as total_records FROM sb_rcm_detail_v;
SELECT '뷰 생성 완료!' as status;
