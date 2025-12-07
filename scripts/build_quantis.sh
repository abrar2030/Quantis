#!/bin/bash

# Quantis Project Build Script
# This script builds the production assets for the API and frontend components.

# Exit immediately if a command exits with a non-zero status, and treat unset variables as an error.
set -euo pipefail

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="${PROJECT_ROOT}/api"
WEB_FRONTEND_DIR="${PROJECT_ROOT}/web-frontend"
MOBILE_FRONTEND_DIR="${PROJECT_ROOT}/mobile-frontend"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Quantis production build process...${NC}"

# --- 1. API Build (Python) ---
echo "----------------------------------------"
echo -e "${BLUE}Building API dependencies...${NC}"
# For Python, "building" typically means ensuring dependencies are installed and potentially compiling Cython/Rust extensions.
# Since the setup script handles dependency installation, this step focuses on ensuring the environment is ready.

# Check for Python virtual environment
PYTHON_VENV="${API_DIR}/venv_quantis_api_py"
if [ ! -d "${PYTHON_VENV}" ]; then
  echo -e "${RED}Error: Python virtual environment not found at ${PYTHON_VENV}.${NC}"
  echo -e "${RED}Please run the setup script first: ${PROJECT_ROOT}/scripts/setup_quantis_env.sh${NC}"
  exit 1
fi

# --- 2. Web Frontend Build ---
echo "----------------------------------------"
echo -e "${BLUE}Building Web Frontend...${NC}"

if [ ! -d "${WEB_FRONTEND_DIR}" ]; then
    echo -e "${RED}Warning: Web Frontend directory ${WEB_FRONTEND_DIR} not found. Skipping build.${NC}"
else
    if [ ! -f "${WEB_FRONTEND_DIR}/package.json" ]; then
        echo -e "${RED}Warning: package.json not found in ${WEB_FRONTEND_DIR}. Skipping build.${NC}"
    else
        echo "Installing/Verifying Web Frontend dependencies..."
        (cd "${WEB_FRONTEND_DIR}" && npm install)
        
        echo "Running Web Frontend production build..."
        # Assuming 'npm run build' is the standard build command
        (cd "${WEB_FRONTEND_DIR}" && npm run build)
        echo -e "${GREEN}Web Frontend build completed. Output in ${WEB_FRONTEND_DIR}/dist (or similar).${NC}"
    fi
fi

# --- 3. Mobile Frontend Build ---
echo "----------------------------------------"
echo -e "${BLUE}Building Mobile Frontend...${NC}"

if [ ! -d "${MOBILE_FRONTEND_DIR}" ]; then
    echo -e "${RED}Warning: Mobile Frontend directory ${MOBILE_FRONTEND_DIR} not found. Skipping build.${NC}"
else
    if [ ! -f "${MOBILE_FRONTEND_DIR}/package.json" ]; then
        echo -e "${RED}Warning: package.json not found in ${MOBILE_FRONTEND_DIR}. Skipping build.${NC}"
    else
        echo "Installing/Verifying Mobile Frontend dependencies..."
        # Check for pnpm usage
        if grep -q '"packageManager": "pnpm' "${MOBILE_FRONTEND_DIR}/package.json" 2>/dev/null; then
            (cd "${MOBILE_FRONTEND_DIR}" && pnpm install)
            BUILD_CMD="pnpm run build"
        else
            (cd "${MOBILE_FRONTEND_DIR}" && npm install)
            BUILD_CMD="npm run build"
        fi
        
        echo "Running Mobile Frontend production build..."
        # Assuming 'run build' is the standard build command
        (cd "${MOBILE_FRONTEND_DIR}" && ${BUILD_CMD})
        echo -e "${GREEN}Mobile Frontend build completed. Output in ${MOBILE_FRONTEND_DIR}/dist (or similar).${NC}"
    fi
fi

echo "----------------------------------------"
echo -e "${GREEN}Quantis production build process finished!${NC}"
echo "The application is now ready for deployment."
