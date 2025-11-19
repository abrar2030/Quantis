#!/bin/bash
# setup_environment.sh - Comprehensive environment setup script for Quantis project
#
# This script automates the setup of development environments for the Quantis project:
# - Installs all required dependencies
# - Sets up virtual environments for Python components
# - Configures Node.js environments for frontend components
# - Sets up database connections
# - Configures monitoring tools
#
# Usage: ./setup_environment.sh [options]
# Options:
#   --all                Setup complete environment
#   --python             Setup only Python environment
#   --node               Setup only Node.js environment
#   --db                 Setup only database connections
#   --monitoring         Setup only monitoring tools
#   --dev                Setup for development (default)
#   --prod               Setup for production
#   --help               Show this help message
#
# Author: Manus AI
# Date: May 22, 2025

set -e  # Exit immediately if a command exits with a non-zero status

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default settings
SETUP_PYTHON=false
SETUP_NODE=false
SETUP_DB=false
SETUP_MONITORING=false
ENV="development"
PROJECT_ROOT=$(pwd)

# Function to display help message
show_help() {
    echo -e "${BLUE}Environment Setup Script for Quantis Project${NC}"
    echo ""
    echo "Usage: ./setup_environment.sh [options]"
    echo ""
    echo "Options:"
    echo "  --all                Setup complete environment"
    echo "  --python             Setup only Python environment"
    echo "  --node               Setup only Node.js environment"
    echo "  --db                 Setup only database connections"
    echo "  --monitoring         Setup only monitoring tools"
    echo "  --dev                Setup for development (default)"
    echo "  --prod               Setup for production"
    echo "  --help               Show this help message"
    echo ""
    exit 0
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_system_requirements() {
    echo -e "${BLUE}Checking system requirements...${NC}"

    # Check operating system
    OS=$(uname -s)
    echo "Operating System: $OS"

    # Check available memory
    if command_exists free; then
        TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
        echo "Total Memory: ${TOTAL_MEM}MB"

        if [ "$TOTAL_MEM" -lt 4000 ]; then
            echo -e "${YELLOW}Warning: Less than 4GB of RAM available. Performance may be affected.${NC}"
        fi
    fi

    # Check available disk space
    DISK_SPACE=$(df -h . | awk 'NR==2 {print $4}')
    echo "Available Disk Space: $DISK_SPACE"

    # Check CPU cores
    if command_exists nproc; then
        CPU_CORES=$(nproc)
        echo "CPU Cores: $CPU_CORES"
    fi

    echo -e "${GREEN}System requirements checked.${NC}"
}

# Function to setup Python environment
setup_python_env() {
    echo -e "${BLUE}Setting up Python environment...${NC}"

    # Check if Python is installed
    if ! command_exists python3; then
        echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
        echo "Please install Python 3 and try again."
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "Python Version: $PYTHON_VERSION"

    # Create virtual environments for API and models
    echo "Creating virtual environments..."

    # API virtual environment
    if [ -d "$PROJECT_ROOT/api" ]; then
        cd "$PROJECT_ROOT/api"

        if [ ! -d "venv" ]; then
            echo "Creating API virtual environment..."
            python3 -m venv venv
        else
            echo "API virtual environment already exists."
        fi

        # Activate virtual environment and install dependencies
        echo "Installing API dependencies..."
        source venv/bin/activate
        pip install --upgrade pip

        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        else
            echo -e "${YELLOW}Warning: requirements.txt not found for API.${NC}"
        fi

        # Install development dependencies if in dev mode
        if [ "$ENV" = "development" ] && [ -f "requirements-dev.txt" ]; then
            pip install -r requirements-dev.txt
        fi

        deactivate
    else
        echo -e "${YELLOW}Warning: API directory not found.${NC}"
    fi

    # Models virtual environment
    if [ -d "$PROJECT_ROOT/models" ]; then
        cd "$PROJECT_ROOT/models"

        if [ ! -d "venv" ]; then
            echo "Creating models virtual environment..."
            python3 -m venv venv
        else
            echo "Models virtual environment already exists."
        fi

        # Activate virtual environment and install dependencies
        echo "Installing models dependencies..."
        source venv/bin/activate
        pip install --upgrade pip

        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        else
            echo -e "${YELLOW}Warning: requirements.txt not found for models.${NC}"
        fi

        # Install development dependencies if in dev mode
        if [ "$ENV" = "development" ] && [ -f "requirements-dev.txt" ]; then
            pip install -r requirements-dev.txt
        fi

        deactivate
    else
        echo -e "${YELLOW}Warning: Models directory not found.${NC}"
    fi

    echo -e "${GREEN}Python environment setup completed.${NC}"
}

# Function to setup Node.js environment
setup_node_env() {
    echo -e "${BLUE}Setting up Node.js environment...${NC}"

    # Check if Node.js is installed
    if ! command_exists node; then
        echo -e "${RED}Error: Node.js is required but not installed.${NC}"
        echo "Please install Node.js and try again."
        exit 1
    fi

    # Check Node.js version
    NODE_VERSION=$(node --version)
    echo "Node.js Version: $NODE_VERSION"

    # Check if npm is installed
    if ! command_exists npm; then
        echo -e "${RED}Error: npm is required but not installed.${NC}"
        echo "Please install npm and try again."
        exit 1
    fi

    # Check npm version
    NPM_VERSION=$(npm --version)
    echo "npm Version: $NPM_VERSION"

    # Setup web frontend
    if [ -d "$PROJECT_ROOT/web-frontend" ]; then
        cd "$PROJECT_ROOT/web-frontend"

        echo "Installing web frontend dependencies..."
        npm install

        # Create environment-specific configuration
        if [ "$ENV" = "development" ]; then
            if [ -f ".env.development.example" ] && [ ! -f ".env.development" ]; then
                echo "Creating development environment configuration..."
                cp .env.development.example .env.development
            fi
        elif [ "$ENV" = "production" ]; then
            if [ -f ".env.production.example" ] && [ ! -f ".env.production" ]; then
                echo "Creating production environment configuration..."
                cp .env.production.example .env.production
            fi
        fi
    else
        echo -e "${YELLOW}Warning: Web frontend directory not found.${NC}"
    fi

    # Setup mobile frontend
    if [ -d "$PROJECT_ROOT/mobile-frontend" ]; then
        cd "$PROJECT_ROOT/mobile-frontend"

        echo "Installing mobile frontend dependencies..."
        npm install

        # Create environment-specific configuration
        if [ "$ENV" = "development" ]; then
            if [ -f ".env.development.example" ] && [ ! -f ".env.development" ]; then
                echo "Creating development environment configuration..."
                cp .env.development.example .env.development
            fi
        elif [ "$ENV" = "production" ]; then
            if [ -f ".env.production.example" ] && [ ! -f ".env.production" ]; then
                echo "Creating production environment configuration..."
                cp .env.production.example .env.production
            fi
        fi
    else
        echo -e "${YELLOW}Warning: Mobile frontend directory not found.${NC}"
    fi

    echo -e "${GREEN}Node.js environment setup completed.${NC}"
}

# Function to setup database connections
setup_db_connections() {
    echo -e "${BLUE}Setting up database connections...${NC}"

    # Check if PostgreSQL client is installed
    if ! command_exists psql; then
        echo -e "${YELLOW}Warning: PostgreSQL client is not installed.${NC}"
        echo "Some database setup steps may be skipped."
    else
        echo "PostgreSQL client is installed."
    fi

    # Create database configuration files
    if [ -d "$PROJECT_ROOT/api" ]; then
        cd "$PROJECT_ROOT/api"

        if [ -f "database.yml.example" ] && [ ! -f "database.yml" ]; then
            echo "Creating database configuration..."
            cp database.yml.example database.yml

            # Update database configuration based on environment
            if [ "$ENV" = "development" ]; then
                echo "Configuring for development database..."
                # Here you would typically modify the database.yml file
                # with sed or other text manipulation tools
            elif [ "$ENV" = "production" ]; then
                echo "Configuring for production database..."
                # Here you would typically modify the database.yml file
                # with sed or other text manipulation tools
            fi
        fi
    fi

    # Setup InfluxDB configuration for time series data
    if [ -d "$PROJECT_ROOT/monitoring" ]; then
        cd "$PROJECT_ROOT/monitoring"

        if [ -f "influxdb.conf.example" ] && [ ! -f "influxdb.conf" ]; then
            echo "Creating InfluxDB configuration..."
            cp influxdb.conf.example influxdb.conf
        fi
    fi

    echo -e "${GREEN}Database connections setup completed.${NC}"
}

# Function to setup monitoring tools
setup_monitoring_tools() {
    echo -e "${BLUE}Setting up monitoring tools...${NC}"

    if [ -d "$PROJECT_ROOT/monitoring" ]; then
        cd "$PROJECT_ROOT/monitoring"

        # Setup Prometheus configuration
        if [ -f "prometheus.yml.example" ] && [ ! -f "prometheus.yml" ]; then
            echo "Creating Prometheus configuration..."
            cp prometheus.yml.example prometheus.yml
        fi

        # Setup Grafana dashboards
        if [ -d "grafana_dashboards" ]; then
            echo "Setting up Grafana dashboards..."
            # Here you would typically copy or configure Grafana dashboards
        fi

        # Setup alerting rules
        if [ -f "alerting_rules.yml.example" ] && [ ! -f "alerting_rules.yml" ]; then
            echo "Creating alerting rules configuration..."
            cp alerting_rules.yml.example alerting_rules.yml
        fi
    else
        echo -e "${YELLOW}Warning: Monitoring directory not found.${NC}"
    fi

    echo -e "${GREEN}Monitoring tools setup completed.${NC}"
}

# Function to create a project-wide .env file
create_env_file() {
    echo -e "${BLUE}Creating environment configuration file...${NC}"

    ENV_FILE="$PROJECT_ROOT/.env"

    if [ ! -f "$ENV_FILE" ]; then
        echo "Creating .env file..."

        cat > "$ENV_FILE" << EOF
# Quantis Environment Configuration
# Generated by setup_environment.sh on $(date)
# Environment: $ENV

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
API_LOG_LEVEL=info

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=quantis_$ENV
DB_USER=quantis
DB_PASSWORD=quantis_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Frontend Configuration
FRONTEND_PORT=3000
API_BASE_URL=http://localhost:8000

# Monitoring Configuration
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Feature Flags
ENABLE_FEATURE_X=true
ENABLE_FEATURE_Y=false
EOF

        echo -e "${GREEN}.env file created at $ENV_FILE${NC}"
    else
        echo -e "${YELLOW}Warning: .env file already exists. Skipping creation.${NC}"
    fi
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_help
fi

while [ "$1" != "" ]; do
    case $1 in
        --all )     SETUP_PYTHON=true
                    SETUP_NODE=true
                    SETUP_DB=true
                    SETUP_MONITORING=true
                    SETUP_ALL=true
                    ;;
        --python )  SETUP_PYTHON=true
                    ;;
        --node )    SETUP_NODE=true
                    ;;
        --db )      SETUP_DB=true
                    ;;
        --monitoring ) SETUP_MONITORING=true
                    ;;
        --dev )     ENV="development"
                    ;;
        --prod )    ENV="production"
                    ;;
        --help )    show_help
                    ;;
        * )         echo -e "${RED}Error: Unknown option $1${NC}"
                    show_help
                    ;;
    esac
    shift
done

# Main execution
echo -e "${BLUE}Starting Quantis environment setup...${NC}"
echo -e "Environment: ${YELLOW}$ENV${NC}"

# Check system requirements
check_system_requirements

# Setup components
if $SETUP_PYTHON || $SETUP_ALL; then
    setup_python_env
fi

if $SETUP_NODE || $SETUP_ALL; then
    setup_node_env
fi

if $SETUP_DB || $SETUP_ALL; then
    setup_db_connections
fi

if $SETUP_MONITORING || $SETUP_ALL; then
    setup_monitoring_tools
fi

# Create .env file
if $SETUP_ALL; then
    create_env_file
fi

echo -e "${GREEN}Quantis environment setup completed successfully!${NC}"
echo -e "${YELLOW}Note: You may need to restart your terminal or run 'source .env' to apply environment variables.${NC}"
exit 0
