-- Add oauth_token_secret column to platform_connections table for OAuth 1.0a support (Twitter)
ALTER TABLE platform_connections 
ADD COLUMN oauth_token_secret TEXT;