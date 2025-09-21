# Project Delivery TODO

## 1. Prepare the Local Environment
- [ ] Verify prerequisites are installed: Docker (+ Compose), Node.js 18+, pnpm, Python 3.11+, and (optional) local PostgreSQL.
- [ ] Create a new repository from the template on GitHub and clone it locally.
- [ ] Run the backend setup wizard (`backend/tools/setup_server.py`) to customize branding, secrets, and environment defaults.
- [ ] Copy `.env.example` to `.env` and update any remaining secrets or provider credentials the wizard did not cover.
- [ ] Start the full dev stack with `make dev` (or `pnpm dev`) and confirm frontend (`http://localhost:5173`) and backend (`http://localhost:8000/docs`) load.
- [ ] Document any configuration details decided during setup (domains, OAuth IDs, SMTP provider, etc.).

## 2. Configure Application Services
- [ ] Review database migration history; create new migrations with `make migration-create MESSAGE="..."` for schema changes.
- [ ] Apply migrations locally via `make migrate` and confirm DB schema matches expectations.
- [ ] If integrating third-party auth or email, populate the corresponding `.env` variables and verify callbacks/SMTP connectivity.
- [ ] Generate updated TypeScript API contracts with `make generate-types` after backend schema changes.

## 3. Quality Checks & Testing
- [ ] Run `make lint` and resolve lint issues; optionally use `make lint-fix` for auto-fixes.
- [ ] Run `make type-check` to ensure TypeScript and Python type safety.
- [ ] Execute backend tests with `make test-backend` (or `cd backend && pytest --cov=app tests/`).
- [ ] Execute frontend unit tests with `make test-frontend` (or `cd frontend && pnpm test`).
- [ ] Run PWA Playwright checks (`cd frontend && npx playwright test pwa.spec.ts`), installing browsers first if needed.
- [ ] Run the full suite (`make test`) before preparing production artifacts.

## 4. Prepare Production Configuration
- [ ] Decide on managed PostgreSQL vs. self-hosted; provision the production database and capture its connection string.
- [ ] Assemble production `.env` values (secure `SECRET_KEY`, `ENVIRONMENT=production`, `DEBUG=false`, external DB URL, OAuth/SMTP creds, domain URLs).
- [ ] Configure domain DNS records (A/AAAA) for the planned VPS and plan subdomains (e.g., `app.yourdomain.com`, `api.yourdomain.com`).
- [ ] Review `docker-compose.prod.yml` and Traefik labels; update hostnames, certificates, and email for ACME/Let's Encrypt as needed.
- [ ] Build production images locally with `make build` and smoke-test via `docker-compose -f docker-compose.prod.yml up` on a staging machine if possible.

## 5. Provision the VPS (DigitalOcean or Hetzner)
- [ ] Create a droplet/server (Ubuntu 22.04 LTS recommended) with sufficient CPU/RAM for the stack.
- [ ] Add SSH keys in the provider control panel for passwordless access.
- [ ] Enable firewall rules: allow SSH (22), HTTP (80), HTTPS (443); close unused ports.
- [ ] Log in as root, create a non-root deploy user, and configure sudo + SSH hardening.
- [ ] Install system packages, Docker Engine, and the Docker Compose plugin following the official convenience script or package repository.
- [ ] (Optional) Configure swap space and unattended upgrades for stability.

## 6. Deploy to Production
- [ ] Clone the repository onto the VPS (or pull from your remote) under the deploy user's home directory.
- [ ] Copy the production `.env` (and any Traefik/Docker secrets files) to the server; store them outside version control but accessible to Compose.
- [ ] Review and adjust `docker-compose.prod.yml` environment variables, volumes, and Traefik labels for the live domains.
- [ ] Start the stack with `docker-compose -f docker-compose.prod.yml up -d` (or `make prod`) and wait for containers to become healthy.
- [ ] Verify Traefik obtained TLS certificates and routes traffic correctly to frontend and backend services.
- [ ] Run initial database migrations on the VPS with `make migrate` (or equivalent Compose exec command).

## 7. Post-Deployment Verification & Maintenance
- [ ] Check service health (`make health`) and inspect logs (`make logs`, `make logs-backend`, `make logs-frontend`).
- [ ] Confirm frontend, API docs, authentication flows, and email delivery work in production.
- [ ] Configure automated backups for the production database (provider-managed or cron-based dumps).
- [ ] Set up monitoring/alerts (provider metrics, uptime checks) and document incident response steps.
- [ ] Schedule regular dependency updates and security reviews; track template updates via upstream remote as described in `README.md`.
- [ ] Record deployment details (server IP, credentials storage location, rotation cadence) for future maintainers.
