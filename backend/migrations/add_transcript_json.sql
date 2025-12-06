-- Migration: Add transcript_json column to interview_sessions table
-- Date: 2025-12-06
-- Description: Adds a transcript_json column to store voice interview transcripts

ALTER TABLE interview_sessions 
ADD COLUMN IF NOT EXISTS transcript_json JSON NULL
COMMENT 'Stores voice interview transcript as JSON array of messages';

-- Note: This is a SQLite-compatible migration
-- For SQLite, use:
-- ALTER TABLE interview_sessions ADD COLUMN transcript_json TEXT;

-- For MySQL/MariaDB, use:
-- ALTER TABLE interview_sessions ADD COLUMN transcript_json JSON NULL;

-- For PostgreSQL, the above statement works as-is

