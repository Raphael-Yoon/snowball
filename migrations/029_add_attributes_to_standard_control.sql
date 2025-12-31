-- ============================================================
-- 기준통제(sb_standard_control)에 attribute 필드 추가
-- 마이그레이션: 029_add_attributes_to_standard_control
-- 작성일: 2025-12-30
-- ============================================================

-- MySQL용 ALTER TABLE 구문
-- 운영 DB에서 직접 실행하세요

USE snowball;  -- 데이터베이스명 확인 후 수정

-- 1. attribute0~9 컬럼 추가
ALTER TABLE sb_standard_control ADD COLUMN attribute0 VARCHAR(100);
ALTER TABLE sb_standard_control ADD COLUMN attribute1 VARCHAR(100);
ALTER TABLE sb_standard_control ADD COLUMN attribute2 VARCHAR(100);
ALTER TABLE sb_standard_control ADD COLUMN attribute3 VARCHAR(100);
ALTER TABLE sb_standard_control ADD COLUMN attribute4 VARCHAR(100);
ALTER TABLE sb_standard_control ADD COLUMN attribute5 VARCHAR(100);
ALTER TABLE sb_standard_control ADD COLUMN attribute6 VARCHAR(100);
ALTER TABLE sb_standard_control ADD COLUMN attribute7 VARCHAR(100);
ALTER TABLE sb_standard_control ADD COLUMN attribute8 VARCHAR(100);
ALTER TABLE sb_standard_control ADD COLUMN attribute9 VARCHAR(100);

-- 2. population_attribute_count 컬럼 추가
ALTER TABLE sb_standard_control ADD COLUMN population_attribute_count INTEGER DEFAULT 2;

-- 3. 변경사항 확인
DESC sb_standard_control;

-- 4. 추가된 컬럼 확인
SELECT
    std_control_id,
    control_code,
    control_name,
    attribute0,
    attribute1,
    attribute2,
    population_attribute_count
FROM sb_standard_control
LIMIT 5;

-- ============================================================
-- 롤백 (필요 시)
-- ============================================================
-- ALTER TABLE sb_standard_control DROP COLUMN attribute0;
-- ALTER TABLE sb_standard_control DROP COLUMN attribute1;
-- ALTER TABLE sb_standard_control DROP COLUMN attribute2;
-- ALTER TABLE sb_standard_control DROP COLUMN attribute3;
-- ALTER TABLE sb_standard_control DROP COLUMN attribute4;
-- ALTER TABLE sb_standard_control DROP COLUMN attribute5;
-- ALTER TABLE sb_standard_control DROP COLUMN attribute6;
-- ALTER TABLE sb_standard_control DROP COLUMN attribute7;
-- ALTER TABLE sb_standard_control DROP COLUMN attribute8;
-- ALTER TABLE sb_standard_control DROP COLUMN attribute9;
-- ALTER TABLE sb_standard_control DROP COLUMN population_attribute_count;
