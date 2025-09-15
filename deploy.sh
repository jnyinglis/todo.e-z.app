#!/bin/bash

# Production Deployment Script
# This script demonstrates how to deploy the application using pre-built images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying Vite+React+FastAPI Template${NC}"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ Please update .env with your actual values before continuing!${NC}"
    exit 1
fi

# Source environment variables
source .env

# Validate required environment variables
required_vars=("GITHUB_REPOSITORY" "IMAGE_TAG" "POSTGRES_PASSWORD" "SECRET_KEY" "DOMAIN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Error: $var is not set in .env file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment variables validated${NC}"

# Pull latest images
echo -e "${YELLOW}📥 Pulling latest images...${NC}"
docker pull ghcr.io/${GITHUB_REPOSITORY}/frontend:${IMAGE_TAG}
docker pull ghcr.io/${GITHUB_REPOSITORY}/backend:${IMAGE_TAG}

# Stop existing services
echo -e "${YELLOW}🛑 Stopping existing services...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}🔍 Checking service health...${NC}"

# Check backend health
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

# Check if Traefik is running
if docker-compose -f docker-compose.prod.yml ps traefik | grep -q "Up"; then
    echo -e "${GREEN}✅ Traefik is running${NC}"
    echo -e "${GREEN}🌐 Application should be available at: https://${DOMAIN}${NC}"
    echo -e "${GREEN}📊 Traefik dashboard: https://traefik.${DOMAIN}${NC}"
else
    echo -e "${RED}❌ Traefik is not running${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo "Services running:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.prod.yml down"