# SchoolAI - AI Mentor Platform

## Project Overview
SchoolAI is an enterprise-grade AI Mentor Platform designed to provide personalized guidance to students by understanding their individual needs, learning styles, and emotional intelligence.

## Technical Architecture

### Backend (FastAPI)
- **FastAPI**: High-performance async API framework.
- **PostgreSQL**: Relational database for structured student and session data.
- **SQLAlchemy (Async)**: ORM for database interactions.
- **JWT Authentication**: Secure, stateless authentication.
- **Pydantic**: Data validation and settings management.

### Frontend (React)
- **Vite**: Ultra-fast build tool.
- **TypeScript**: Static typing for reliability.
- **Tailwind CSS**: Utility-first styling.
- **Framer Motion**: Smooth, high-performance animations.
- **Zustand**: Lightweight state management.
- **React Query**: Server state management and caching.

## Directory Structure
- `frontend/`: React application.
- `backend/`: FastAPI application.
- `database/`: Database scripts and migrations.
- `docker/`: Dockerfiles and container configurations.

## Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js (for local frontend development)
- Python 3.11+ (for local backend development)

### Running with Docker
```bash
docker-compose up --build
```

### Manual Setup
1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
