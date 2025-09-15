# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a full-stack monorepo template with:
- **Frontend**: Vite + React with TypeScript, mobile-responsive design
- **Backend**: FastAPI with SQLAlchemy ORM and Pydantic models
- **Database**: PostgreSQL
- **Proxy**: Traefik (production only)
- **Package Manager**: pnpm
- **Authentication**: Google, Apple, and Magic Link email authentication

## Development Commands

### Frontend (Vite + React)
```bash
cd frontend
pnpm install
pnpm dev          # Start development server with hot reload
pnpm build        # Build for production
pnpm preview      # Preview production build
pnpm lint         # Run ESLint
pnpm type-check   # Run TypeScript type checking
```

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload  # Start development server with hot reload
pytest                    # Run tests
pytest --hypothesis-show-statistics  # Run tests with Hypothesis
python generate_types.py  # Generate TypeScript types from OpenAPI spec
```

### Docker Development
```bash
docker-compose -f docker-compose.dev.yml up  # Local development with hot reload
docker-compose -f docker-compose.prod.yml up # Production build with Traefik
```

### Database
```bash
# Run migrations (when implemented)
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Key Architecture Patterns

### Type Safety
- FastAPI uses Pydantic models for request/response validation
- OpenAPI schema generates TypeScript types for frontend consumption
- Shared type definitions ensure API contract consistency

### Authentication Flow
- Multi-provider authentication (Google, Apple, Magic Link)
- JWT token-based authentication
- Frontend redirects and state management for auth flows

### Build Information
- Both frontend and backend generate build-info files during build
- Includes version, build number, git info, and environment (test/prod)
- Used for deployment tracking and debugging

### Container Strategy
- Development: Hot reload enabled, source mounted as volumes
- Production: Optimized builds, Traefik proxy for routing
- GHCR-ready images for container registry deployment

### Testing Strategy
- Backend: pytest with Hypothesis for property-based testing
- Frontend: Vitest/Jest for unit tests, Playwright/Cypress for e2e
- API contract testing between frontend and backend

## Project Structure
```
├── frontend/          # Vite + React application
├── backend/           # FastAPI application
├── docker-compose.dev.yml   # Development environment
├── docker-compose.prod.yml  # Production environment
└── shared/            # Shared types and utilities (if implemented)
```

## Development Workflow

1. **Local Development**: Use `docker-compose.dev.yml` for full-stack development
2. **API Development**: Generate TypeScript types after backend schema changes
3. **Testing**: Run both frontend and backend tests before commits
4. **Production**: Build optimized containers for deployment to GHCR

## Mobile Considerations
- Frontend must be responsive and mobile-friendly
- Touch-friendly UI components and interactions
- Responsive breakpoints for various screen sizes
- A TODO.md will always be maintained it should be updated as task are completed.