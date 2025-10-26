# Design Document

## Overview

Quflux is a cloud-native social media management platform built with a microservices-oriented architecture. The system leverages FastAPI for the backend API, Supabase for authentication and data persistence, Celery for background job processing, and Strands SDK for AI-powered content generation. The platform supports multi-platform publishing with a focus on scalability, reliability, and user experience.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Next.js Frontend]
    end
    
    subgraph "API Layer"
        API[FastAPI Backend]
        AUTH[Supabase Auth]
    end
    
    subgraph "Processing Layer"
        CELERY[Celery Workers]
        SCHEDULER[Celery Beat Scheduler]
        AI[Strands AI Agent]
        NANO[Google Nano Banana]
    end
    
    subgraph "Data Layer"
        DB[(Supabase PostgreSQL)]
        CACHE[(Supabase KV Cache)]
        S3[(AWS S3 Media Storage)]
    end
    
    subgraph "External APIs"
        TWITTER[X/Twitter API]
        LINKEDIN[LinkedIn API]
        META[Meta Graph API]
        SENDGRID[SendGrid Email]
    end
    
    UI --> API
    API --> AUTH
    API --> DB
    API --> CACHE
    API --> CELERY
    CELERY --> AI
    CELERY --> NANO
    CELERY --> TWITTER
    CELERY --> LINKEDIN
    CELERY --> META
    CELERY --> SENDGRID
    CELERY --> S3
    SCHEDULER --> CELERY
```

### System Components

1. **Frontend Application**: Next.js with TailwindCSS providing responsive UI
2. **API Gateway**: FastAPI handling HTTP requests, authentication, and business logic
3. **Background Processing**: Celery workers for asynchronous task processing
4. **AI Content Generation**: Strands SDK agent for caption/hashtag generation and Google Nano Banana for image creation/editing
5. **Data Persistence**: Supabase PostgreSQL for structured data
6. **Caching Layer**: Supabase key-value store using dedicated cache table
7. **Job Queuing**: Celery with PostgreSQL as broker using SQLAlchemy
8. **Media Storage**: AWS S3 for images and videos
9. **External Integrations**: Social platform APIs and email service

## Components and Interfaces

### 1. Authentication Service

**Purpose**: Handle user authentication and session management using Supabase

**Key Components**:
- `AuthService`: Manages user registration, login, and session validation
- `UserRepository`: Database operations for user data
- `SessionManager`: Supabase-based session storage using cache table

**Interfaces**:
```python
class AuthService:
    async def register_user(self, email: str, password: str) -> User
    async def authenticate_user(self, email: str, password: str) -> AuthToken
    async def validate_session(self, token: str) -> User
    async def logout_user(self, token: str) -> bool
```

### 2. Platform Connection Service

**Purpose**: Manage OAuth connections to social media platforms

**Key Components**:
- `PlatformConnectionService`: Handles OAuth flows and token management
- `PlatformRepository`: Stores connection credentials securely
- `OAuthHandlers`: Platform-specific OAuth implementations

**Interfaces**:
```python
class PlatformConnectionService:
    async def initiate_oauth(self, platform: str, user_id: str) -> OAuthURL
    async def complete_oauth(self, platform: str, code: str, user_id: str) -> Connection
    async def refresh_token(self, connection_id: str) -> Connection
    async def disconnect_platform(self, connection_id: str) -> bool
```

### 3. Post Composition Service

**Purpose**: Handle post creation, editing, and media management

**Key Components**:
- `PostService`: Core post management logic
- `MediaService`: Handle file uploads and processing
- `LinkPreviewService`: Generate OpenGraph previews

**Interfaces**:
```python
class PostService:
    async def create_post(self, user_id: str, content: PostContent) -> Post
    async def update_post(self, post_id: str, content: PostContent) -> Post
    async def delete_post(self, post_id: str) -> bool
    async def get_user_posts(self, user_id: str, filters: PostFilters) -> List[Post]
```

### 4. AI Content Generation Service

**Purpose**: Generate captions, hashtags, content suggestions, and create/edit images

**Key Components**:
- `AIContentAgent`: Strands agent configured for content generation
- `ImageGenerationService`: Google Nano Banana integration for image creation and editing
- `ContentGenerationService`: Service layer for AI operations
- `PromptTemplates`: Structured prompts for different content types

**Interfaces**:
```python
class ContentGenerationService:
    async def generate_caption(self, context: ContentContext) -> str
    async def suggest_hashtags(self, content: str, platform: str) -> List[str]
    async def generate_content_ideas(self, topic: str, audience: str) -> List[str]

class ImageGenerationService:
    async def generate_image(self, prompt: str, style: str) -> ImageResult
    async def edit_image(self, image_url: str, edit_prompt: str) -> ImageResult
    async def create_social_graphic(self, text: str, template: str) -> ImageResult
```

**Strands Agent Configuration**:
```python
from strands import Agent, tool

@tool
async def generate_social_caption(
    content_type: str,
    topic: str,
    platform: str,
    tone: str = "professional"
) -> str:
    """Generate engaging social media captions.
    
    Args:
        content_type: Type of content (image, video, link, text)
        topic: Main topic or theme
        platform: Target platform (twitter, linkedin, instagram, facebook)
        tone: Desired tone (professional, casual, humorous, inspirational)
    """
    # Implementation using Strands SDK
    pass

@tool
async def generate_image_with_nano_banana(
    prompt: str,
    style: str = "realistic",
    dimensions: str = "1024x1024"
) -> str:
    """Generate images using Google Nano Banana.
    
    Args:
        prompt: Description of the image to generate
        style: Image style (realistic, artistic, cartoon, etc.)
        dimensions: Image dimensions (1024x1024, 1920x1080, etc.)
    """
    # Implementation using Google Nano Banana API
    pass

ai_agent = Agent(
    tools=[generate_social_caption, suggest_hashtags, generate_image_with_nano_banana],
    name="Quflux Content Generator"
)
```

### 5. Scheduling Service

**Purpose**: Manage post scheduling and queue management

**Key Components**:
- `SchedulingService`: Handle schedule creation and management
- `QueueManager`: Manage Celery job queues with PostgreSQL broker
- `CalendarService`: Provide calendar views and conflict detection

**Interfaces**:
```python
class SchedulingService:
    async def schedule_post(self, post_id: str, schedule_time: datetime, platforms: List[str]) -> Schedule
    async def update_schedule(self, schedule_id: str, new_time: datetime) -> Schedule
    async def cancel_schedule(self, schedule_id: str) -> bool
    async def get_user_schedule(self, user_id: str, date_range: DateRange) -> List[Schedule]
```

### 6. Publishing Service

**Purpose**: Execute scheduled posts across multiple platforms

**Key Components**:
- `PublishingService`: Orchestrate publishing operations
- `PlatformPublishers`: Platform-specific publishing logic
- `RetryManager`: Handle failed publications with exponential backoff

**Interfaces**:
```python
class PublishingService:
    async def publish_post(self, schedule_id: str) -> PublishResult
    async def publish_immediately(self, post_id: str, platforms: List[str]) -> List[PublishResult]
    async def retry_failed_publication(self, publication_id: str) -> PublishResult
```

### 7. Notification Service

**Purpose**: Send notifications about post status and system events

**Key Components**:
- `NotificationService`: Manage notification delivery
- `EmailService`: SendGrid integration for email notifications
- `WebSocketService`: Real-time in-app notifications

**Interfaces**:
```python
class NotificationService:
    async def send_publication_success(self, user_id: str, post_details: PostDetails) -> bool
    async def send_publication_failure(self, user_id: str, error_details: ErrorDetails) -> bool
    async def send_real_time_notification(self, user_id: str, notification: Notification) -> bool
```

## Data Models

### Core Entities

```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class PlatformType(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class User(BaseModel):
    id: str
    email: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class PlatformConnection(BaseModel):
    id: str
    user_id: str
    platform: PlatformType
    platform_user_id: str
    platform_username: str
    access_token: str  # Encrypted
    refresh_token: Optional[str]  # Encrypted
    expires_at: Optional[datetime]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class MediaFile(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    file_size: int
    s3_key: str
    s3_url: str
    created_at: datetime

class Post(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    content: str
    media_files: List[str] = []  # MediaFile IDs
    link_url: Optional[str]
    link_preview: Optional[Dict[str, Any]]
    ai_generated: bool = False
    status: PostStatus = PostStatus.DRAFT
    created_at: datetime
    updated_at: datetime

class Schedule(BaseModel):
    id: str
    post_id: str
    user_id: str
    scheduled_time: datetime
    platforms: List[PlatformType]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class Publication(BaseModel):
    id: str
    schedule_id: str
    platform: PlatformType
    platform_post_id: Optional[str]
    status: str  # success, failed, pending
    error_message: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
```

### Database Schema

```sql
-- Users table (managed by Supabase Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Cache table for key-value storage
CREATE TABLE cache_store (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Celery job queue tables (using SQLAlchemy broker)
CREATE TABLE celery_taskmeta (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,
    result BYTEA,
    date_done TIMESTAMP WITH TIME ZONE,
    traceback TEXT
);

CREATE TABLE celery_tasksetmeta (
    id SERIAL PRIMARY KEY,
    taskset_id VARCHAR(255) UNIQUE NOT NULL,
    result BYTEA,
    date_done TIMESTAMP WITH TIME ZONE
);

-- Platform connections
CREATE TABLE platform_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_user_id VARCHAR(255) NOT NULL,
    platform_username VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL, -- Encrypted
    refresh_token TEXT,         -- Encrypted
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, platform, platform_user_id)
);

-- Media files
CREATE TABLE media_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    s3_url VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Posts
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT NOT NULL,
    media_files JSONB DEFAULT '[]',
    link_url VARCHAR(1000),
    link_preview JSONB,
    ai_generated BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Schedules
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    platforms JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Publications
CREATE TABLE publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID REFERENCES schedules(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_platform_connections_user_id ON platform_connections(user_id);
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_schedules_user_id ON schedules(user_id);
CREATE INDEX idx_schedules_scheduled_time ON schedules(scheduled_time);
CREATE INDEX idx_publications_schedule_id ON publications(schedule_id);
```

## Error Handling

### Error Categories

1. **Authentication Errors**: Invalid credentials, expired tokens, unauthorized access
2. **Validation Errors**: Invalid input data, missing required fields
3. **Platform API Errors**: Rate limiting, API downtime, invalid tokens
4. **System Errors**: Database connectivity, Redis unavailability, S3 failures
5. **Business Logic Errors**: Scheduling conflicts, insufficient permissions

### Error Response Format

```python
class ErrorResponse(BaseModel):
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str

# Example error responses
{
    "error_code": "PLATFORM_API_ERROR",
    "error_message": "Failed to publish to Twitter due to rate limiting",
    "error_details": {
        "platform": "twitter",
        "retry_after": 900,
        "rate_limit_reset": "2024-01-01T15:30:00Z"
    },
    "timestamp": "2024-01-01T14:30:00Z",
    "request_id": "req_123456"
}
```

### Retry Strategy

```python
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 300.0  # 5 minutes
    exponential_base: float = 2.0
    jitter: bool = True

# Celery configuration with PostgreSQL broker
from celery import Celery

celery_app = Celery(
    'quflux',
    broker='sqlalchemy+postgresql://user:pass@host:port/dbname',
    backend='db+postgresql://user:pass@host:port/dbname'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'publish_post_task': {'queue': 'publishing'},
        'generate_content_task': {'queue': 'ai_generation'},
    }
)

# Celery task with retry logic
@celery_app.task(bind=True, max_retries=3)
def publish_post_task(self, schedule_id: str):
    try:
        # Publishing logic
        pass
    except PlatformAPIError as exc:
        # Exponential backoff with jitter
        countdown = min(
            RetryConfig.base_delay * (RetryConfig.exponential_base ** self.request.retries),
            RetryConfig.max_delay
        )
        if RetryConfig.jitter:
            countdown *= (0.5 + random.random() * 0.5)
        
        raise self.retry(exc=exc, countdown=countdown)
```

## Testing Strategy

### Testing Pyramid

1. **Unit Tests (70%)**
   - Service layer logic
   - Data model validation
   - Utility functions
   - AI content generation tools

2. **Integration Tests (20%)**
   - Database operations
   - External API integrations
   - Celery task execution
   - Authentication flows

3. **End-to-End Tests (10%)**
   - Complete user workflows
   - Multi-platform publishing
   - Scheduling and execution
   - Error scenarios

### Test Configuration

```python
# pytest configuration
@pytest.fixture
async def test_client():
    """FastAPI test client with test database"""
    app.dependency_overrides[get_database] = get_test_database
    app.dependency_overrides[get_celery] = get_test_celery
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_strands_agent():
    """Mock Strands agent for testing AI features"""
    with patch('services.ai_service.ai_agent') as mock_agent:
        mock_agent.invoke_async.return_value = "Generated caption"
        yield mock_agent

# Example test
async def test_generate_caption(test_client, mock_strands_agent):
    response = await test_client.post(
        "/api/v1/ai/generate-caption",
        json={"content_type": "image", "topic": "technology", "platform": "twitter"}
    )
    assert response.status_code == 200
    assert "Generated caption" in response.json()["caption"]
```

### Mock Strategy

- **External APIs**: Mock all social platform APIs using `responses` library
- **AI Services**: Mock Strands agent responses for predictable testing
- **Background Jobs**: Use Celery's eager mode for synchronous execution in tests
- **File Storage**: Mock S3 operations with local file system

## Deployment Architecture

### Infrastructure Components

```mermaid
graph TB
    subgraph "AWS Cloud"
        subgraph "Compute"
            APPRUNNER_API[AWS App Runner<br/>FastAPI Backend]
            APPRUNNER_FRONTEND[AWS App Runner<br/>Next.js Frontend]
            LAMBDA[AWS Lambda<br/>Celery Workers]
        end
        
        subgraph "Storage"
            S3[AWS S3<br/>Media Files]
        end
        
        subgraph "External Services"
            SUPABASE[Supabase<br/>Database & Auth]
            SENDGRID[SendGrid<br/>Email Service]
        end
    end
    
    APPRUNNER_FRONTEND --> APPRUNNER_API
    APPRUNNER_API --> SUPABASE
    APPRUNNER_API --> S3
    LAMBDA --> SUPABASE
    LAMBDA --> S3
    LAMBDA --> SENDGRID
```

### Terraform Configuration Structure

```
infrastructure/
├── main.tf                 # Main configuration
├── variables.tf           # Input variables
├── outputs.tf            # Output values
├── modules/
│   ├── app-runner-api/   # FastAPI backend
│   ├── app-runner-frontend/ # Next.js frontend
│   ├── lambda/           # Celery workers
│   ├── s3/              # Media storage
│   └── iam/             # IAM roles and policies
└── environments/
    ├── dev/
    ├── staging/
    └── production/
```

### Environment Configuration

```python
# Environment-specific settings
class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Celery broker (uses same database as main app)
    celery_broker_url: str  # SQLAlchemy PostgreSQL URL
    
    # AWS
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    s3_bucket_name: str
    
    # External APIs
    twitter_api_key: str
    twitter_api_secret: str
    linkedin_client_id: str
    linkedin_client_secret: str
    meta_app_id: str
    meta_app_secret: str
    sendgrid_api_key: str
    
    # Strands SDK
    strands_api_key: str
    
    # Google Nano Banana
    google_nano_banana_api_key: str
    
    # Security
    jwt_secret_key: str
    encryption_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Monitoring and Observability

1. **Application Metrics**: Custom metrics for post publishing success rates, AI generation latency
2. **Infrastructure Metrics**: AWS CloudWatch for App Runner and Lambda
3. **Error Tracking**: Sentry integration for error monitoring and alerting
4. **Logging**: Structured logging with correlation IDs for request tracing
5. **Health Checks**: Endpoint monitoring for all critical services

This design provides a scalable, maintainable foundation for the Quflux social media management platform, with clear separation of concerns, robust error handling, and comprehensive testing strategies.