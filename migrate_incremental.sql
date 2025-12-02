-- ============================================================================
-- Snowball 증분 마이그레이션 스크립트 (MySQL)
-- ============================================================================
-- 실행 방법: mysql -u username -p snowball < migrate_incremental.sql
-- 또는:     mysql -u username -p snowball
--           > source migrate_incremental.sql
-- ============================================================================

USE snowball;

-- 마이그레이션 히스토리 테이블 확인/생성
CREATE TABLE IF NOT EXISTS sb_migration_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INT,
    status VARCHAR(20) DEFAULT 'success'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 마이그레이션 001: review_comment 컬럼 추가
-- ============================================================================

-- 이미 적용되었는지 확인
SET @migration_001_exists = (
    SELECT COUNT(*)
    FROM sb_migration_history
    WHERE version = '001'
);

-- 컬럼이 없으면 추가
SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
    AND table_name = 'sb_operation_evaluation_line'
    AND column_name = 'review_comment'
);

SET @sql_001 = IF(@column_exists = 0 AND @migration_001_exists = 0,
    'ALTER TABLE sb_operation_evaluation_line ADD COLUMN review_comment TEXT',
    'SELECT "Migration 001 already applied or column exists" AS status'
);

PREPARE stmt FROM @sql_001;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 마이그레이션 기록
INSERT IGNORE INTO sb_migration_history (version, name, status)
VALUES ('001', 'add_review_comment_to_operation_line', 'success');

-- ============================================================================
-- 마이그레이션 002: design_comment 컬럼 추가
-- ============================================================================

-- 이미 적용되었는지 확인
SET @migration_002_exists = (
    SELECT COUNT(*)
    FROM sb_migration_history
    WHERE version = '002'
);

-- 컬럼이 없으면 추가
SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
    AND table_name = 'sb_design_evaluation_line'
    AND column_name = 'design_comment'
);

SET @sql_002 = IF(@column_exists = 0 AND @migration_002_exists = 0,
    'ALTER TABLE sb_design_evaluation_line ADD COLUMN design_comment TEXT',
    'SELECT "Migration 002 already applied or column exists" AS status'
);

PREPARE stmt FROM @sql_002;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 마이그레이션 기록
INSERT IGNORE INTO sb_migration_history (version, name, status)
VALUES ('002', 'add_design_comment_to_design_line', 'success');

-- ============================================================================
-- 향후 마이그레이션은 여기에 추가
-- ============================================================================

-- 예시:
-- SET @column_exists = (
--     SELECT COUNT(*)
--     FROM information_schema.columns
--     WHERE table_schema = DATABASE()
--     AND table_name = 'your_table'
--     AND column_name = 'new_column'
-- );
--
-- SET @sql_003 = IF(@column_exists = 0,
--     'ALTER TABLE your_table ADD COLUMN new_column VARCHAR(100)',
--     'SELECT "Column already exists" AS status'
-- );
--
-- PREPARE stmt FROM @sql_003;
-- EXECUTE stmt;
-- DEALLOCATE PREPARE stmt;
--
-- INSERT IGNORE INTO sb_migration_history (version, name, status)
-- VALUES ('003', 'add_new_column', 'success');

-- ============================================================================
-- 완료 메시지
-- ============================================================================

SELECT '증분 마이그레이션 완료!' AS message;

-- 적용된 마이그레이션 목록
SELECT
    version,
    name,
    applied_at,
    status
FROM sb_migration_history
ORDER BY version;
