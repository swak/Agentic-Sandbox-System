#!/bin/bash

# Agentic Sandbox System - Setup Script
# This script validates prerequisites and initializes the system

set -e  # Exit on error

echo "============================================"
echo "Agentic Sandbox System - Setup"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ===================================================================
# 1. Check Prerequisites
# ===================================================================

echo "Step 1/5: Checking prerequisites..."
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker Compose found"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running.${NC}"
    echo "Please start Docker Desktop or the Docker daemon."
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker daemon is running"

echo ""

# ===================================================================
# 2. Environment Configuration
# ===================================================================

echo "Step 2/5: Configuring environment..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Please edit .env and add your API keys:${NC}"
    echo "  - OPENAI_API_KEY=your-key-here"
    echo "  - ANTHROPIC_API_KEY=your-key-here"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
else
    echo -e "${GREEN}✓${NC} .env file found"
fi

# Validate API keys
source .env
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Warning: No API keys found in .env${NC}"
    echo "You'll need at least one API key (OpenAI or Anthropic) to use the system."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo -e "${GREEN}✓${NC} OpenAI API key configured"
    fi
    if [ ! -z "$ANTHROPIC_API_KEY" ]; then
        echo -e "${GREEN}✓${NC} Anthropic API key configured"
    fi
fi

echo ""

# ===================================================================
# 3. Create Directories
# ===================================================================

echo "Step 3/5: Creating directories..."
echo ""

mkdir -p configs
mkdir -p backend/app/api
mkdir -p backend/app/models
mkdir -p backend/app/services
mkdir -p backend/app/schemas
mkdir -p backend/app/utils
mkdir -p frontend/src/components
mkdir -p frontend/src/pages
mkdir -p frontend/src/services
mkdir -p frontend/src/context
mkdir -p database

echo -e "${GREEN}✓${NC} Directories created"
echo ""

# ===================================================================
# 4. Build Docker Images
# ===================================================================

echo "Step 4/5: Building Docker images..."
echo ""

echo "This may take several minutes on first run..."
docker-compose build

echo -e "${GREEN}✓${NC} Docker images built successfully"
echo ""

# ===================================================================
# 5. Start Services
# ===================================================================

echo "Step 5/5: Starting services..."
echo ""

docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Services started successfully"
else
    echo -e "${RED}Error: Some services failed to start${NC}"
    echo "Run 'docker-compose logs' to see error details"
    exit 1
fi

echo ""

# ===================================================================
# Setup Complete
# ===================================================================

echo "============================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "============================================"
echo ""
echo "Your Agentic Sandbox System is now running:"
echo ""
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f          # View logs"
echo "  docker-compose ps               # Check status"
echo "  docker-compose down             # Stop services"
echo "  docker-compose restart          # Restart services"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Click 'Create New Agent'"
echo "  3. Configure your first agent"
echo "  4. Start chatting!"
echo ""
echo "For help, see README.md or visit the documentation."
echo ""
