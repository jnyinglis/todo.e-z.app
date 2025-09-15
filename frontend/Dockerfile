# Frontend Dockerfile
FROM node:24-alpine as build

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install pnpm
RUN npm install -g pnpm@8

# Install dependencies (use --no-frozen-lockfile for dependency updates)
RUN pnpm install --no-frozen-lockfile

# Copy source code
COPY . .

# Build arguments for build info
ARG BUILD_VERSION=unknown
ARG BUILD_NUMBER=unknown
ARG GIT_COMMIT=unknown
ARG ENVIRONMENT=production

# Create build info
RUN mkdir -p public && printf '{\n  "version": "%s",\n  "buildNumber": "%s",\n  "gitCommit": "%s",\n  "environment": "%s",\n  "buildTime": "%s"\n}\n' \
  "$BUILD_VERSION" "$BUILD_NUMBER" "$GIT_COMMIT" "$ENVIRONMENT" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > public/build-info.json

# Build the application
RUN pnpm build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]