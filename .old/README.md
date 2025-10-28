# Quflux - Social Media Management Platform

Quflux is a comprehensive social media management automation platform that enables users to create, schedule, and automatically publish content across multiple social media platforms with AI-powered content generation capabilities.

## Features

- **Multi-Platform Support**: X/Twitter, LinkedIn, Instagram, Facebook
- **AI Content Generation**: Powered by Strands SDK and Google Nano Banana
- **Automated Scheduling**: Queue and publish posts at optimal times
- **Rich Media Support**: Images, videos, and link previews
- **Real-time Notifications**: Email and in-app notifications
- **Analytics Dashboard**: Track post performance and engagement

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Supabase**: Authentication and database
- **Celery**: Background task processing
- **Redis**: Message broker and caching
- **PostgreSQL**: Primary database
- **AWS S3**: Media file storage
- **Strands SDK**: AI content generation

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd quflux
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   
   # Frontend
   cp frontend/.env.example frontend/.env
   ```

3. **Start the development environment**
   ```bash
   docker-compose up -d
   ```

4. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Development Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
quflux/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── core/               # Core configuration
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   ├── repositories/       # Data access layer
│   ├── tasks/              # Celery tasks
│   └── main.py             # Application entry point
├── frontend/               # Next.js frontend
│   ├── app/                # App Router pages
│   ├── components/         # React components
│   ├── lib/                # Utility libraries
│   ├── types/              # TypeScript types
│   └── hooks/              # Custom React hooks
├── database/               # Database initialization
├── docker-compose.yml      # Development environment
└── README.md
```

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anon key
- `CELERY_BROKER_URL`: Redis URL for Celery
- `AWS_ACCESS_KEY_ID`: AWS credentials
- `STRANDS_API_KEY`: Strands SDK API key

### Frontend (.env)
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_SUPABASE_URL`: Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase anon key

## Development Commands

### Backend
```bash
# Run development server
uvicorn main:app --reload

# Run Celery worker
celery -A celery_app worker --loglevel=info

# Run Celery beat scheduler
celery -A celery_app beat --loglevel=info
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.