#!/bin/bash

# Quantis Project Test Script
# This script runs all unit and integration tests for the project.

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

echo -e "${BLUE}Starting Quantis test suite...${NC}"

# --- 1. Python Backend Tests (API, Models, Code) ---
echo "----------------------------------------"
echo -e "${BLUE}Running Python Backend Tests (pytest)...${NC}"

# Check for Python virtual environment
PYTHON_VENV="${API_DIR}/venv_quantis_api_py"
if [ ! -d "${PYTHON_VENV}" ]; then
  echo -e "${RED}Error: Python virtual environment not found at ${PYTHON_VENV}.${NC}"
  echo -e "${RED}Please run the setup script first: ${PROJECT_ROOT}/scripts/setup_quantis_env.sh${NC}"
  exit 1
fi

# Activate venv and run tests
(
  # shellcheck source=/dev/null
  source "${PYTHON_VENV}/bin/activate"
  
  # Ensure pytest is installed
  if ! command -v pytest &> /dev/null; then
    echo "Installing pytest..."
    pip install pytest pytest-cov
  fi
  
  # Run tests from the project root
  cd "${PROJECT_ROOT}"
  
  # Assuming tests are in the 'tests' directory
  if [ -d "tests" ]; then
    echo "Executing pytest with coverage..."
    # Use --cov-report=term-missing to show coverage details
    pytest --cov=api --cov=models --cov=code --cov-report=term-missing tests/
    echo -e "${GREEN}Python Backend Tests completed.${NC}"
  else
    echo -e "${RED}Warning: 'tests' directory not found. Skipping Python tests.${NC}"
  fi
)

# --- 2. Web Frontend Tests ---
echo "----------------------------------------"
echo -e "${BLUE}Running Web Frontend Tests...${NC}"

if [ ! -d "${WEB_FRONTEND_DIR}" ]; then
    echo -e "${RED}Warning: Web Frontend directory ${WEB_FRONTEND_DIR} not found. Skipping tests.${NC}"
else
    if [ ! -f "${WEB_FRONTEND_DIR}/package.json" ]; then
        echo -e "${RED}Warning: package.json not found in ${WEB_FRONTEND_DIR}. Skipping tests.${NC}"
    else
        # Assuming 'npm test' is the standard test command
        if grep -q '"test":' "${WEB_FRONTEND_DIR}/package.json"; then
            echo "Executing Web Frontend tests (npm test)..."
            (cd "${WEB_FRONTEND_DIR}" && npm test)
            echo -e "${GREEN}Web Frontend Tests completed.${NC}"
        else
            echo -e "${RED}Warning: 'test' script not found in ${WEB_FRONTEND_DIR}/package.json. Skipping tests.${NC}"
        fi
    fi
fi

# --- 3. Mobile Frontend Tests ---
echo "----------------------------------------"
echo -e "${BLUE}Running Mobile Frontend Tests...${NC}"

if [ ! -d "${MOBILE_FRONTEND_DIR}" ]; then
    echo -e "${RED}Warning: Mobile Frontend directory ${MOBILE_FRONTEND_DIR} not found. Skipping tests.${NC}"
else
    if [ ! -f "${MOBILE_FRONTEND_DIR}/package.json" ]; then
        echo -e "${RED}Warning: package.json not found in ${MOBILE_FRONTEND_DIR}. Skipping tests.${NC}"
    else
        # Check for pnpm usage
        if grep -q '"packageManager": "pnpm' "${MOBILE_FRONTEND_DIR}/package.json" 2>/dev/null; then
            TEST_CMD="pnpm test"
        else
            TEST_CMD="npm test"
        fi
        
        # Assuming 'run test' is the standard test command
        if grep -q '"test":' "${MOBILE_FRONTEND_DIR}/package.json"; then
            echo "Executing Mobile Frontend tests (${TEST_CMD})..."
            (cd "${MOBILE_FRONTEND_DIR}" && ${TEST_CMD})
            echo -e "${GREEN}Mobile Frontend Tests completed.${NC}"
        else
            echo -e "${RED}Warning: 'test' script not found in ${MOBILE_FRONTEND_DIR}/package.json. Skipping tests.${NC}"
        fi
    fi
fi

echo "----------------------------------------"
echo -e "${GREEN}Quantis test suite finished!${NC}"
