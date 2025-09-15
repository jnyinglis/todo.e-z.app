# Vite + React + FastAPI + PostgreSQL Template

A modern, production-ready full-stack template with TypeScript, authentication, PWA capabilities, and an interactive setup wizard.

## 🚀 Features

- **Frontend**: React 18 + Vite + TypeScript with responsive design
- **Backend**: FastAPI + SQLAlchemy 2.0 + Alembic migrations
- **Database**: PostgreSQL with async support
- **Authentication**: Google, Apple, and Magic Link email authentication with secure httpOnly cookies
- **PWA**: Full Progressive Web App with offline support, service worker, and install prompts
- **SEO**: Comprehensive SEO optimization with meta tags, Open Graph, and structured data
- **Development**: Docker Compose with hot reload
- **Production**: Optimized Docker builds with Traefik proxy
- **Testing**: Comprehensive pytest suite + Playwright for PWA testing
- **Type Safety**: Full-stack TypeScript with API contract generation
- **Setup Wizard**: Interactive configuration tool for personalized app setup

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended for development)
- **Node.js 18+** and **pnpm** (for local development)
- **Python 3.11+** (for local development)
- **PostgreSQL** (if running locally without Docker)

## 🛠️ Quick Start

### GitHub Template Usage (Recommended)

1. **Create from Template**: Click "Use this template" → "Create a new repository" on GitHub
2. **Clone your new repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_NEW_REPO_NAME.git
   cd YOUR_NEW_REPO_NAME
   ```

3. **Run the Setup Wizard**:
   ```bash
   # Install Python dependencies for the setup tool
   cd backend/tools
   pip install fastapi uvicorn python-dotenv pydantic

   # Start the interactive setup wizard
   python setup_server.py
   ```

4. **Configure your app**: Open http://127.0.0.1:5050 and complete the 5-step setup:
   - 🎯 **App Identity**: Name, branding, and colors
   - 🔐 **Environment & Security**: Auto-generated secure credentials
   - 🌐 **Domain & Deployment**: Production configuration
   - 🔑 **Authentication Setup**: OAuth provider guidance
   - ✅ **Review & Apply**: Apply all configurations

5. **Start developing**:
   ```bash
   # Return to project root and start development
   cd ../..
   make dev
   ```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

```bash
# Copy environment configuration
cp .env.example .env

# Start development environment
make dev

# Or build and start fresh
make dev-build
```

### Local Development (Without Docker)

```bash
# Install dependencies
make install

# Setup backend environment
make install-backend

# Start database (Docker)
docker-compose -f docker-compose.dev.yml up db -d

# Start backend (in terminal 1)
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Start frontend (in terminal 2)
cd frontend
pnpm dev
```

## ✨ New Features

### 🎯 Interactive Setup Wizard

The setup wizard (`backend/tools/setup_server.py`) provides a comprehensive configuration experience:

- **App Identity Configuration**: Customize app name, description, and branding
- **Automatic Slug Generation**: Converts app names to database/container-friendly slugs
- **Secure Credential Generation**: Auto-generates JWT secrets and database passwords
- **File Updates**: Automatically updates package.json, manifest.json, icons, and SEO defaults
- **Real-time Preview**: See configuration changes as you make them

### 📱 Progressive Web App (PWA)

Full PWA support with modern capabilities:

- **Service Worker**: Network-first API caching, cache-first static assets
- **Install Prompts**: Native app installation on mobile and desktop
- **Offline Support**: App works offline with cached resources
- **App Icons**: Customizable SVG icons that update with your branding
- **Web App Manifest**: Configurable app metadata and theme colors

### 🔍 SEO Optimization

Enterprise-grade SEO features:

- **Dynamic Meta Tags**: Configurable title, description, and keywords
- **Open Graph**: Social media sharing optimization
- **Twitter Cards**: Twitter-specific metadata
- **Structured Data**: JSON-LD with Schema.org markup
- **Dynamic Sitemaps**: Auto-generated XML sitemaps
- **Robots.txt**: SEO-friendly crawler directives

### 🔐 Enhanced Security

Production-ready security implementations:

- **httpOnly Cookies**: XSS-protected token storage
- **Secure Headers**: CSP, HSTS, and security headers
- **Environment Variables**: Secure credential management
- **CORS Configuration**: Environment-based origin control

## 🔧 Configuration

### Setup Wizard (Recommended)

Use the interactive setup wizard for easy configuration:

```bash
cd backend/tools
python setup_server.py
# Open http://127.0.0.1:5050
```

### Manual Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/template_db
DATABASE_URL_SYNC=postgresql://postgres:postgres@db:5432/template_db

# JWT Configuration
SECRET_KEY=your-super-secure-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Apple OAuth (optional)
APPLE_CLIENT_ID=your-apple-client-id
APPLE_CLIENT_SECRET=your-apple-client-secret
APPLE_KEY_ID=your-apple-key-id
APPLE_TEAM_ID=your-apple-team-id

# Email/SMTP (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Application
APP_NAME="Your App Name"
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development
DEBUG=true
```

### Authentication Setup

#### Google Authentication
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google+ API
3. Create OAuth 2.0 credentials
4. Add `http://localhost:5173` to authorized origins
5. Add your client ID and secret to `.env`

#### Apple Authentication
1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Create an App ID and Services ID
3. Configure Sign in with Apple
4. Add your credentials to `.env`

## 📊 Database Management

### Migrations

```bash
# Create a new migration
make migration-create MESSAGE="Add user preferences"

# Run migrations
make migrate

# Check current migration
make migration-current

# View migration history
make migration-history

# Rollback one migration
make migration-rollback
```

### Database Operations

```bash
# Access database shell
make shell-db

# Backup database
make backup-db

# View database logs
make logs-db
```

## 🧪 Testing

### Backend Testing

```bash
# Run all backend tests
make test-backend

# Run tests with coverage
cd backend && python -m pytest --cov=app tests/

# Run specific test categories
python -m pytest -m unit          # Unit tests only
python -m pytest -m integration   # Integration tests only
python -m pytest -m auth          # Authentication tests only
```

### Frontend Testing

```bash
# Run frontend tests
make test-frontend

# Or directly
cd frontend && pnpm test
```

### PWA Testing

```bash
# Run Playwright PWA tests
cd frontend
npx playwright test pwa.spec.ts

# Install browsers first if needed
npx playwright install
```

The PWA test suite covers:
- Service worker registration and activation
- PWA install prompt functionality
- Offline mode detection and handling
- App manifest validation
- Icon availability and loading
- Cache strategy verification

### Full Test Suite

```bash
# Run all tests (frontend + backend + PWA)
make test
```

## 🏗️ Development Workflow

### Code Quality

```bash
# Run linting
make lint

# Fix linting issues
make lint-fix

# Run type checking
make type-check
```

### API Development

```bash
# Generate TypeScript types from OpenAPI
make generate-types

# View API documentation
# Visit http://localhost:8000/docs (Swagger UI)
# Visit http://localhost:8000/redoc (ReDoc)
```

### Container Management

```bash
# View service status
make ps

# View logs
make logs              # All services
make logs-backend      # Backend only
make logs-frontend     # Frontend only
make logs-db          # Database only

# Shell access
make shell-backend    # Backend container
make shell-frontend   # Frontend container

# Restart services
make restart

# Stop services
make stop

# Clean up everything
make clean
```

## 🚀 Production Deployment

### Build Production Images

```bash
# Build optimized production images
make build

# Or build specific services
docker build -t your-app-frontend ./frontend
docker build -t your-app-backend ./backend
```

### Deploy with Docker Compose

```bash
# Start production environment
make prod

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configuration

Production deployments should:

1. **Set secure environment variables**:
   ```env
   SECRET_KEY=a-very-secure-random-key
   ENVIRONMENT=production
   DEBUG=false
   ```

2. **Use external PostgreSQL**:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@prod-db-host:5432/dbname
   ```

3. **Configure proper domains**:
   ```env
   FRONTEND_URL=https://yourdomain.com
   BACKEND_URL=https://api.yourdomain.com
   ```

### Health Checks

```bash
# Check service health
make health
```

## 📁 Project Structure

```
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   │   ├── SEOHead.tsx  # SEO meta tags component
│   │   │   └── PWAInstallPrompt.tsx # PWA install UI
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   ├── utils/           # Utilities
│   │   │   └── pwa.ts       # PWA management utilities
│   │   └── types/           # TypeScript types
│   ├── public/              # Static assets
│   │   ├── manifest.json    # PWA manifest
│   │   ├── sw.js            # Service worker
│   │   ├── icon-*.svg       # App icons
│   │   └── robots.txt       # SEO robots file
│   ├── tests/               # Frontend tests
│   │   └── pwa.spec.ts      # PWA Playwright tests
│   └── package.json         # Frontend dependencies
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   └── seo.py       # SEO endpoints (sitemap, robots)
│   │   ├── core/            # Core functionality
│   │   │   └── security.py  # Security utilities
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── config/          # Configuration
│   ├── alembic/             # Database migrations
│   ├── tests/               # Test suite
│   │   ├── unit/            # Unit tests
│   │   ├── integration/     # Integration tests
│   │   └── fixtures/        # Test fixtures
│   ├── tools/               # Development tools
│   │   ├── setup_server.py  # Interactive setup wizard
│   │   └── ui/              # Setup wizard UI
│   │       ├── index.html   # Wizard interface
│   │       └── wizard.js    # Wizard functionality
│   └── requirements.txt     # Backend dependencies
│
├── docker-compose.dev.yml    # Development environment
├── docker-compose.prod.yml   # Production environment
├── .env.example             # Environment template
├── Makefile                 # Development commands
├── TODO.md                  # Project progress tracking
└── README.md                # This file
```

## 🔧 Available Commands

Run `make help` to see all available commands:

```bash
make help                    # Show available commands
make setup                   # Complete project setup
make dev                     # Start development environment
make test                    # Run all tests (backend + frontend + PWA)
make lint                    # Run code linting
make build                   # Build production images
make clean                   # Clean up containers and dependencies
```

## 🎨 Template Customization

### Using as a GitHub Template

This repository is designed to be used as a GitHub template:

1. **Click "Use this template"** on the GitHub repository page
2. **Create your new repository** with a clean git history
3. **Run the setup wizard** to customize your application:
   - App name, description, and branding
   - Secure credential generation
   - PWA theme colors and icons
   - Production domain configuration
4. **Start developing** your unique application

### What Gets Customized

The setup wizard automatically updates:

- **`package.json`**: App name and description
- **`manifest.json`**: PWA metadata, colors, and branding
- **App Icons**: SVG files with your app's initials and colors
- **SEO Defaults**: Meta tags, structured data, and canonical URLs
- **Environment Variables**: Secure keys and configuration
- **Database Names**: App-specific database and container naming

### Maintaining Template Updates

To get updates from the original template:

```bash
# Add the template repository as upstream
git remote add template https://github.com/original/template-repo.git

# Fetch template updates
git fetch template

# Merge updates (resolve conflicts as needed)
git merge template/main

# Or cherry-pick specific commits
git cherry-pick <commit-hash>
```

## 🛡️ Security Considerations

### Development
- JWT tokens are signed but not encrypted
- CORS is configured for development
- Debug mode is enabled

### Production
- Use strong, random SECRET_KEY
- Configure proper CORS origins
- Set DEBUG=false
- Use HTTPS for all communications
- Implement rate limiting
- Regular security updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test thoroughly
4. Commit: `git commit -am 'Add your feature'`
5. Push: `git push origin feature/your-feature`
6. Create a Pull Request

### Development Guidelines

- Follow existing code style (use `make lint`)
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check if database is running
make ps
# Restart database
docker-compose -f docker-compose.dev.yml restart db
```

**Frontend Build Issues**
```bash
# Clear node_modules and reinstall
cd frontend && rm -rf node_modules && pnpm install
```

**Backend Import Errors**
```bash
# Rebuild backend container
make dev-build
```

**Migration Issues**
```bash
# Check migration status
make migration-current
# Reset migrations (destructive)
make migration-rollback
```

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review Docker logs: `make logs`
- Verify environment configuration: `cat .env`
- Ensure all prerequisites are installed

## 📈 Performance Tips

- Use `make dev` for hot reload during development
- Run `make type-check` before committing
- Use `make clean` to free up disk space
- Monitor resource usage with `docker stats`

## 🔄 Updates

To update the template:

```bash
git pull origin main
make clean
make setup
```

---

**Happy coding!** 🎉

For more detailed information, check the documentation in the `instructions/` directory.