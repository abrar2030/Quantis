#!/bin/bash
# unified_build.sh - Comprehensive build script for Quantis project
# 
# This script automates the build process for all components of the Quantis project:
# - API (Python backend)
# - Models (Python ML models)
# - Web Frontend (React/TypeScript)
# - Mobile Frontend (React Native)
#
# Usage: ./unified_build.sh [options]
# Options:
#   --all                Build all components
#   --api                Build only API
#   --models             Build only models
#   --web                Build only web frontend
#   --mobile             Build only mobile frontend
#   --clean              Clean build artifacts before building
#   --prod               Build for production
#   --dev                Build for development (default)
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
BUILD_API=false
BUILD_MODELS=false
BUILD_WEB=false
BUILD_MOBILE=false
CLEAN_BUILD=false
ENV="development"
PROJECT_ROOT=$(pwd)

# Function to display help message
show_help() {
    echo -e "${BLUE}Unified Build Script for Quantis Project${NC}"
    echo ""
    echo "Usage: ./unified_build.sh [options]"
    echo ""
    echo "Options:"
    echo "  --all                Build all components"
    echo "  --api                Build only API"
    echo "  --models             Build only models"
    echo "  --web                Build only web frontend"
    echo "  --mobile             Build only mobile frontend"
    echo "  --clean              Clean build artifacts before building"
    echo "  --prod               Build for production"
    echo "  --dev                Build for development (default)"
    echo "  --help               Show this help message"
    echo ""
    exit 0
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check required dependencies
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    # Check Python
    if ! command_exists python3; then
        echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
        exit 1
    fi
    
    # Check Node.js for frontend builds
    if ($BUILD_WEB || $BUILD_MOBILE) && ! command_exists node; then
        echo -e "${RED}Error: Node.js is required for frontend builds but not installed.${NC}"
        exit 1
    fi
    
    # Check npm for frontend builds
    if ($BUILD_WEB || $BUILD_MOBILE) && ! command_exists npm; then
        echo -e "${RED}Error: npm is required for frontend builds but not installed.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}All required dependencies are installed.${NC}"
}

# Function to clean build artifacts
clean_build() {
    echo -e "${BLUE}Cleaning build artifacts...${NC}"
    
    if $BUILD_API || $BUILD_ALL; then
        echo "Cleaning API build artifacts..."
        rm -rf api/__pycache__ api/**/__pycache__
        find api -name "*.pyc" -delete
    fi
    
    if $BUILD_MODELS || $BUILD_ALL; then
        echo "Cleaning models build artifacts..."
        rm -rf models/__pycache__ models/**/__pycache__
        find models -name "*.pyc" -delete
    fi
    
    if $BUILD_WEB || $BUILD_ALL; then
        echo "Cleaning web frontend build artifacts..."
        rm -rf web-frontend/build web-frontend/node_modules/.cache
    fi
    
    if $BUILD_MOBILE || $BUILD_ALL; then
        echo "Cleaning mobile frontend build artifacts..."
        rm -rf mobile-frontend/build mobile-frontend/node_modules/.cache
    fi
    
    echo -e "${GREEN}Build artifacts cleaned successfully.${NC}"
}

# Function to build API
build_api() {
    echo -e "${BLUE}Building API...${NC}"
    
    cd "$PROJECT_ROOT/api"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing API dependencies..."
    pip install -r requirements.txt
    
    # Run any build steps (like compiling protobuf, etc.)
    if [ -f "setup.py" ]; then
        echo "Running API setup..."
        pip install -e .
    fi
    
    # Deactivate virtual environment
    deactivate
    
    echo -e "${GREEN}API built successfully.${NC}"
}

# Function to build models
build_models() {
    echo -e "${BLUE}Building models...${NC}"
    
    cd "$PROJECT_ROOT/models"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "Installing model dependencies..."
    pip install -r requirements.txt
    
    # Run any model-specific build steps
    if [ -f "setup.py" ]; then
        echo "Running models setup..."
        pip install -e .
    fi
    
    # Deactivate virtual environment
    deactivate
    
    echo -e "${GREEN}Models built successfully.${NC}"
}

# Function to build web frontend
build_web_frontend() {
    echo -e "${BLUE}Building web frontend...${NC}"
    
    cd "$PROJECT_ROOT/web-frontend"
    
    # Install dependencies
    echo "Installing web frontend dependencies..."
    npm install
    
    # Build the web frontend
    echo "Building web frontend for $ENV environment..."
    if [ "$ENV" = "production" ]; then
        npm run build
    else
        npm run build:dev
    fi
    
    echo -e "${GREEN}Web frontend built successfully.${NC}"
}

# Function to build mobile frontend
build_mobile_frontend() {
    echo -e "${BLUE}Building mobile frontend...${NC}"
    
    cd "$PROJECT_ROOT/mobile-frontend"
    
    # Install dependencies
    echo "Installing mobile frontend dependencies..."
    npm install
    
    # Build the mobile frontend
    echo "Building mobile frontend for $ENV environment..."
    if [ "$ENV" = "production" ]; then
        npm run build
    else
        npm run build:dev
    fi
    
    echo -e "${GREEN}Mobile frontend built successfully.${NC}"
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_help
fi

while [ "$1" != "" ]; do
    case $1 in
        --all )     BUILD_API=true
                    BUILD_MODELS=true
                    BUILD_WEB=true
                    BUILD_MOBILE=true
                    BUILD_ALL=true
                    ;;
        --api )     BUILD_API=true
                    ;;
        --models )  BUILD_MODELS=true
                    ;;
        --web )     BUILD_WEB=true
                    ;;
        --mobile )  BUILD_MOBILE=true
                    ;;
        --clean )   CLEAN_BUILD=true
                    ;;
        --prod )    ENV="production"
                    ;;
        --dev )     ENV="development"
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
echo -e "${BLUE}Starting Quantis unified build process...${NC}"
echo -e "Environment: ${YELLOW}$ENV${NC}"

# Check dependencies
check_dependencies

# Clean build artifacts if requested
if $CLEAN_BUILD; then
    clean_build
fi

# Build components
if $BUILD_API; then
    build_api
fi

if $BUILD_MODELS; then
    build_models
fi

if $BUILD_WEB; then
    build_web_frontend
fi

if $BUILD_MOBILE; then
    build_mobile_frontend
fi

echo -e "${GREEN}Quantis build process completed successfully!${NC}"
exit 0
