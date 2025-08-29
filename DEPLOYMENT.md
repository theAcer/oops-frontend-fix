# Deployment Guide

## Development Setup

### Prerequisites
- Docker and Docker Compose installed
- Git

### Quick Start
1. Clone the repository
2. Run the development environment:
   \`\`\`bash
   make dev
   # or
   docker-compose up --build
   \`\`\`

### Services
- **Frontend**: http://localhost:3000 (Next.js)
- **Backend API**: http://localhost:8000 (FastAPI)
- **Database**: PostgreSQL on port 5432
- **Redis**: Redis on port 6379

### Environment Variables
Create `.env` files in both frontend and backend directories:

**Backend (.env)**:
\`\`\`
DATABASE_URL=postgresql://postgres:password@db:5432/zidisha_db
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
AFRICAS_TALKING_API_KEY=your-at-key
AFRICAS_TALKING_USERNAME=your-at-username
\`\`\`

**Frontend (.env.local)**:
\`\`\`
NEXT_PUBLIC_API_URL=http://localhost:8000
\`\`\`

## Production Deployment

### With Nginx (Recommended)
\`\`\`bash
make prod
\`\`\`

This starts all services including an Nginx reverse proxy on port 80.

### Manual Commands
\`\`\`bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up
make clean
\`\`\`

## Database Management

### Access Database
\`\`\`bash
make db-shell
\`\`\`

### Backup Database
\`\`\`bash
docker-compose exec db pg_dump -U postgres zidisha_db > backup.sql
\`\`\`

### Restore Database
\`\`\`bash
docker-compose exec -T db psql -U postgres zidisha_db < backup.sql
\`\`\`

## Troubleshooting

### Common Issues
1. **Port conflicts**: Change ports in docker-compose.yml
2. **Database connection**: Ensure DATABASE_URL matches service name
3. **CORS issues**: Update CORS_ORIGINS in API service

### Useful Commands
\`\`\`bash
# Restart specific service
docker-compose restart api

# Rebuild specific service
docker-compose build frontend

# View service logs
make logs-api
make logs-frontend
