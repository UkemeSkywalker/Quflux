-- Add password_hash column to users table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'password_hash') THEN
        ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
    END IF;
END $$;

-- Update existing users with a default password hash (they'll need to reset)
-- This is just for development - in production you'd handle this differently
UPDATE users 
SET password_hash = '$2b$12$dummy.hash.for.existing.users.that.need.to.reset.password'
WHERE password_hash IS NULL;

-- Make password_hash NOT NULL after updating existing records
ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;