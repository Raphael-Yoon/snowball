-- Migration: Add evaluation_session to sb_internal_assessment
-- Date: 2025-10-19
-- Purpose: 하나의 RCM에 여러 설계평가 세션별 내부평가를 지원하도록 개선

-- Step 1: Create new table with updated schema
CREATE TABLE sb_internal_assessment_new (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rcm_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    evaluation_session TEXT DEFAULT 'DEFAULT',  -- 설계평가 세션 식별자 (예: 'DS_2024_Q1')
    step INTEGER NOT NULL,  -- 1:RCM평가, 2:설계평가, 3:운영평가
    progress_data TEXT,  -- JSON 형태의 진행상황 데이터
    status TEXT DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed'
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
    FOREIGN KEY (user_id) REFERENCES sb_user (user_id),
    UNIQUE(rcm_id, user_id, evaluation_session, step)
);

-- Step 2: Migrate existing data (기존 데이터는 DEFAULT 세션으로)
INSERT INTO sb_internal_assessment_new
    (assessment_id, rcm_id, user_id, evaluation_session, step, progress_data, status, created_date, updated_date)
SELECT
    assessment_id,
    rcm_id,
    user_id,
    'DEFAULT' as evaluation_session,  -- 기존 데이터는 DEFAULT 세션
    step,
    progress_data,
    status,
    created_date,
    updated_date
FROM sb_internal_assessment;

-- Step 3: Drop old table
DROP TABLE sb_internal_assessment;

-- Step 4: Rename new table to original name
ALTER TABLE sb_internal_assessment_new RENAME TO sb_internal_assessment;

-- Step 5: Update migration history
INSERT INTO sb_migration_history (version, name, status)
VALUES (
    '20251019_001',
    'add_evaluation_session_to_internal_assessment',
    'success'
);
