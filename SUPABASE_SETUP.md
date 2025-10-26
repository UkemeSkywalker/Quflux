# Supabase Setup Guide

Quflux uses Supabase as the primary database and authentication provider. This guide explains how to set up your Supabase project and configure the environment variables.

## 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project
3. Wait for the project to be fully provisioned

## 2. Get Your Supabase Credentials

From your Supabase project dashboard:

### Project URL and Keys
- **SUPABASE_URL**: Found in Settings > API > Project URL
- **SUPABASE_KEY**: Found in Settings > API > Project API keys > `anon` `public`
- **SUPABASE_SERVICE_KEY**: Found in Settings > API > Project API keys > `service_role` `secret`

### Database Connection String
- **SUPABASE_DB_URL**: Found in Settings > Database > Connection string > URI
  - Format: `postgresql://postgres:[YOUR_PASSWORD]@db.[project-ref].supabase.co:5432/postgres`
  - Replace `[YOUR_PASSWORD]` with your database password
  - Replace `[project-ref]` with your project reference ID
  - **Note**: Use the raw PostgreSQL connection string - the app will automatically convert it for different uses

## 3. Configure Environment Variables

Update your `backend/.env` file with your Supabase credentials:

```env
# Supabase (serves as our database)
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
SUPABASE_DB_URL=postgresql://postgres:[YOUR_PASSWORD]@db.[project-ref].supabase.co:5432/postgres

# Note: DATABASE_URL, CELERY_BROKER_URL, and CELERY_RESULT_BACKEND are automatically 
# generated from SUPABASE_DB_URL in the Settings class
```

## 4. Frontend Configuration

Update your `frontend/.env` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://[project-ref].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 5. Database Schema Setup

You have two options to create the database tables:

### Option A: Manual SQL Script (Recommended)
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `database/init.sql`
4. Click "Run" to execute the script

### Option B: Automatic Creation
The application can automatically create tables when you start the FastAPI server, but this requires additional permissions.

The schema includes:

- `users` - User accounts (managed by Supabase Auth)
- `platform_connections` - Social media platform connections
- `posts` - User posts and content
- `schedules` - Post scheduling information
- `publications` - Publication results and status
- `media_files` - Uploaded media files
- `cache_store` - Key-value cache for sessions and temporary data
- `celery_taskmeta` - Celery task metadata
- `celery_tasksetmeta` - Celery task set metadata

## 6. Authentication Setup

Supabase handles user authentication. Configure your authentication providers in the Supabase dashboard:

1. Go to Authentication > Providers
2. Enable Email authentication
3. Optionally enable social providers (Google, GitHub, etc.)

## 7. Row Level Security (RLS)

For production, enable Row Level Security on your tables:

1. Go to Database > Tables
2. For each table, enable RLS
3. Create policies to ensure users can only access their own data

## 8. Testing the Connection

Run the setup test to verify everything is configured correctly:

```bash
make test-setup
```

This will test:
- Database connectivity
- Supabase client initialization
- All core dependencies

## Notes

- **Single Database**: We use Supabase PostgreSQL for everything (main database, Celery broker, cache)
- **Authentication**: Supabase handles user registration, login, and session management
- **Real-time**: Supabase provides real-time subscriptions for live updates
- **Storage**: We use AWS S3 for media files, but Supabase Storage could be used as an alternative