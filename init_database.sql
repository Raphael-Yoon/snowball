-- ============================================================================
-- Snowball 데이터베이스 초기화 스크립트 (MySQL)
-- ============================================================================
-- 실행 방법: mysql -u username -p < init_database.sql
-- 또는:     mysql -u username -p
--           > source init_database.sql
-- ============================================================================

-- 데이터베이스 생성
DROP DATABASE IF EXISTS snowball;
CREATE DATABASE snowball CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE snowball;

-- ============================================================================
-- 테이블 생성
-- ============================================================================

-- 1. sb_user
CREATE TABLE sb_user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255),
    user_name VARCHAR(100) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50),
    admin_flag VARCHAR(1),
    effective_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_end_date TIMESTAMP NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_date TIMESTAMP NULL,
    otp_code VARCHAR(10),
    otp_expires_at TIMESTAMP NULL,
    otp_attempts INT DEFAULT 0,
    otp_method VARCHAR(20),
    ai_review_count INT DEFAULT 0,
    ai_review_limit INT DEFAULT 3
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. sb_rcm
CREATE TABLE sb_rcm (
    rcm_id INT AUTO_INCREMENT PRIMARY KEY,
    rcm_name VARCHAR(255) NOT NULL,
    description TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    is_active VARCHAR(1) DEFAULT 'Y',
    completion_date TIMESTAMP NULL,
    original_filename VARCHAR(255),
    control_category VARCHAR(50) DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES sb_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. sb_standard_control
CREATE TABLE sb_standard_control (
    std_control_id INT AUTO_INCREMENT PRIMARY KEY,
    control_category VARCHAR(100) NOT NULL,
    control_code VARCHAR(50) NOT NULL,
    control_name VARCHAR(255) NOT NULL,
    control_description TEXT,
    ai_review_prompt TEXT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. sb_rcm_detail
CREATE TABLE sb_rcm_detail (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    rcm_id INT NOT NULL,
    control_code VARCHAR(50) NOT NULL,
    control_name VARCHAR(255) NOT NULL,
    control_description TEXT,
    key_control VARCHAR(50),
    control_frequency VARCHAR(50),
    control_type VARCHAR(50),
    control_nature VARCHAR(50),
    population TEXT,
    population_completeness_check TEXT,
    population_count VARCHAR(50),
    test_procedure TEXT,
    mapped_std_control_id INT,
    mapped_date TIMESTAMP NULL,
    mapped_by INT,
    ai_review_status VARCHAR(50) DEFAULT 'not_reviewed',
    ai_review_recommendation TEXT,
    ai_reviewed_date TIMESTAMP NULL,
    ai_reviewed_by INT,
    mapping_status VARCHAR(50),
    control_category VARCHAR(50) DEFAULT 'ITGC',
    recommended_sample_size INT DEFAULT NULL,
    process_area TEXT,
    risk_description TEXT,
    risk_impact VARCHAR(50),
    risk_likelihood VARCHAR(50),
    control_owner VARCHAR(255),
    control_performer VARCHAR(255),
    evidence_type VARCHAR(100),
    attribute0 VARCHAR(100),
    attribute1 VARCHAR(100),
    attribute2 VARCHAR(100),
    attribute3 VARCHAR(100),
    attribute4 VARCHAR(100),
    attribute5 VARCHAR(100),
    attribute6 VARCHAR(100),
    attribute7 VARCHAR(100),
    attribute8 VARCHAR(100),
    attribute9 VARCHAR(100),
    population_attribute_count INT DEFAULT 2,
    FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
    FOREIGN KEY (mapped_std_control_id) REFERENCES sb_standard_control (std_control_id),
    FOREIGN KEY (mapped_by) REFERENCES sb_user (user_id),
    FOREIGN KEY (ai_reviewed_by) REFERENCES sb_user (user_id),
    UNIQUE KEY unique_rcm_control (rcm_id, control_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. sb_lookup
CREATE TABLE sb_lookup (
    lookup_code VARCHAR(50) NOT NULL,
    lookup_name VARCHAR(255) NOT NULL,
    description TEXT,
    lookup_type VARCHAR(50) NOT NULL,
    KEY idx_lookup_type (lookup_type),
    KEY idx_lookup_code (lookup_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. sb_design_evaluation_header
CREATE TABLE sb_design_evaluation_header (
    header_id INT AUTO_INCREMENT PRIMARY KEY,
    rcm_id INT NOT NULL,
    user_id INT NOT NULL,
    evaluation_session VARCHAR(255) NOT NULL,
    evaluation_status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    total_controls INT DEFAULT 0,
    evaluated_controls INT DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_date TIMESTAMP NULL,
    FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
    FOREIGN KEY (user_id) REFERENCES sb_user (user_id),
    UNIQUE KEY unique_rcm_session (rcm_id, evaluation_session)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. sb_design_evaluation_line
CREATE TABLE sb_design_evaluation_line (
    line_id INT AUTO_INCREMENT PRIMARY KEY,
    header_id INT NOT NULL,
    control_code VARCHAR(50) NOT NULL,
    control_sequence INT DEFAULT 1,
    description_adequacy TEXT,
    improvement_suggestion TEXT,
    overall_effectiveness VARCHAR(50),
    evaluation_evidence TEXT,
    evaluation_rationale TEXT,
    design_comment TEXT,
    recommended_actions TEXT,
    evaluation_date TIMESTAMP NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    no_occurrence TINYINT DEFAULT 0,
    no_occurrence_reason TEXT,
    FOREIGN KEY (header_id) REFERENCES sb_design_evaluation_header (header_id) ON DELETE CASCADE,
    UNIQUE KEY unique_header_control (header_id, control_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. sb_operation_evaluation_header
CREATE TABLE sb_operation_evaluation_header (
    header_id INT AUTO_INCREMENT PRIMARY KEY,
    rcm_id INT NOT NULL,
    user_id INT NOT NULL,
    evaluation_session VARCHAR(255) NOT NULL,
    design_evaluation_session VARCHAR(255) NOT NULL,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_date TIMESTAMP NULL,
    evaluation_status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    evaluated_controls INT DEFAULT 0,
    total_controls INT DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
    FOREIGN KEY (user_id) REFERENCES sb_user (user_id),
    UNIQUE KEY unique_rcm_eval_sessions (rcm_id, evaluation_session, design_evaluation_session)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. sb_operation_evaluation_line
CREATE TABLE sb_operation_evaluation_line (
    line_id INT AUTO_INCREMENT PRIMARY KEY,
    header_id INT NOT NULL,
    control_code VARCHAR(50) NOT NULL,
    control_sequence INT,
    sample_size INT DEFAULT 0,
    exception_count INT DEFAULT 0,
    exception_details TEXT,
    conclusion VARCHAR(50),
    improvement_plan TEXT,
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    population_path TEXT,
    samples_path TEXT,
    test_results_path TEXT,
    population_count INT DEFAULT 0,
    last_updated TIMESTAMP NULL,
    sample_details TEXT,
    no_occurrence TINYINT DEFAULT 0,
    no_occurrence_reason TEXT,
    mitigating_factors TEXT,
    review_comment TEXT,
    FOREIGN KEY (header_id) REFERENCES sb_operation_evaluation_header(header_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. sb_evaluation_sample
CREATE TABLE sb_evaluation_sample (
    sample_id INT AUTO_INCREMENT PRIMARY KEY,
    line_id INT,
    sample_number INT,
    evidence TEXT,
    has_exception TINYINT DEFAULT 0,
    mitigation TEXT,
    evaluation_type VARCHAR(50) DEFAULT 'operation',
    attribute0 TEXT,
    attribute1 TEXT,
    attribute2 TEXT,
    attribute3 TEXT,
    attribute4 TEXT,
    attribute5 TEXT,
    attribute6 TEXT,
    attribute7 TEXT,
    attribute8 TEXT,
    attribute9 TEXT,
    FOREIGN KEY (line_id) REFERENCES sb_operation_evaluation_line (line_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. sb_user_rcm
CREATE TABLE sb_user_rcm (
    mapping_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    rcm_id INT NOT NULL,
    permission_type VARCHAR(50),
    granted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by INT,
    is_active VARCHAR(1),
    last_updated TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. sb_user_activity_log
CREATE TABLE sb_user_activity_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_email VARCHAR(255),
    user_name VARCHAR(100),
    action_type VARCHAR(50) NOT NULL,
    page_name VARCHAR(255),
    url_path VARCHAR(500),
    ip_address VARCHAR(50),
    user_agent TEXT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    additional_info TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. sb_rcm_standard_mapping
CREATE TABLE sb_rcm_standard_mapping (
    mapping_id INT AUTO_INCREMENT PRIMARY KEY,
    rcm_id INT NOT NULL,
    control_code VARCHAR(50) NOT NULL,
    std_control_id INT NOT NULL,
    mapping_confidence DECIMAL(5,2) DEFAULT 0,
    mapping_type VARCHAR(50),
    mapped_by INT,
    mapping_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active VARCHAR(1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. sb_rcm_completeness_eval
CREATE TABLE sb_rcm_completeness_eval (
    eval_id INT AUTO_INCREMENT PRIMARY KEY,
    rcm_id INT NOT NULL,
    eval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_controls INT DEFAULT 0,
    mapped_controls INT DEFAULT 0,
    missing_fields_count INT DEFAULT 0,
    completeness_score DECIMAL(5,2) DEFAULT 0,
    eval_details TEXT,
    eval_by INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. sb_internal_assessment
CREATE TABLE sb_internal_assessment (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    rcm_id INT NOT NULL,
    user_id INT NOT NULL,
    evaluation_session VARCHAR(255),
    step INT NOT NULL,
    progress_data TEXT,
    status VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 16. sb_request
CREATE TABLE sb_request (
    request_id INT,
    request_type VARCHAR(100),
    request_file VARCHAR(500),
    request_date VARCHAR(50),
    return_yn VARCHAR(1),
    client_name VARCHAR(255),
    email_address VARCHAR(255),
    request_content TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 17. sb_user_request
CREATE TABLE sb_user_request (
    company_name VARCHAR(255),
    user_name VARCHAR(100),
    user_email VARCHAR(255),
    interface_yn VARCHAR(1),
    creation_date VARCHAR(50),
    request_id INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 18. sb_user_log
CREATE TABLE sb_user_log (
    user_id INT,
    log_date VARCHAR(50),
    log_type VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 19. sb_migration_history
CREATE TABLE sb_migration_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INT,
    status VARCHAR(20) DEFAULT 'success'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 뷰 생성
-- ============================================================================

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
    d.mapping_status,
    d.control_category,
    d.recommended_sample_size,
    d.population_attribute_count,
    d.attribute0,
    d.attribute1,
    d.attribute2,
    d.attribute3,
    d.attribute4,
    d.attribute5,
    d.attribute6,
    d.attribute7,
    d.attribute8,
    d.attribute9,
    d.control_frequency AS control_frequency_code,
    d.control_type AS control_type_code,
    d.control_nature AS control_nature_code,
    lf.lookup_name AS control_frequency_name,
    lt.lookup_name AS control_type_name,
    ln.lookup_name AS control_nature_name
FROM sb_rcm_detail d
LEFT JOIN sb_lookup lk ON lk.lookup_type = 'key_control'
    AND UPPER(lk.lookup_code) = UPPER(d.key_control)
LEFT JOIN sb_lookup lf ON lf.lookup_type = 'control_frequency'
    AND UPPER(lf.lookup_code) = UPPER(d.control_frequency)
LEFT JOIN sb_lookup lt ON lt.lookup_type = 'control_type'
    AND UPPER(lt.lookup_code) = UPPER(d.control_type)
LEFT JOIN sb_lookup ln ON ln.lookup_type = 'control_nature'
    AND UPPER(ln.lookup_code) = UPPER(d.control_nature);

-- ============================================================================
-- 마이그레이션 히스토리 초기화
-- ============================================================================

INSERT INTO sb_migration_history (version, name, status)
VALUES ('000', 'initial_database_setup', 'success');

-- ============================================================================
-- 완료
-- ============================================================================

SELECT '데이터베이스 초기화 완료!' AS message;
SELECT 'review_comment, design_comment 컬럼 포함됨' AS info;
