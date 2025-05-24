#!/bin/bash

# Quantis Project Setup Script (Comprehensive)

# Exit immediately if a command exits with a non-zero status.
set -e

# Prerequisites (ensure these are installed):
# - Python 3.8+ (the script will use python3.11 available in the environment)
# - pip (Python package installer)
# - Node.js 14+ (for frontend components)
# - npm (Node package manager)
# - Docker and Docker Compose (optional, for containerized deployment as mentioned in README)

echo "Starting Quantis project setup..."

PROJECT_DIR="/home/ubuntu/projects_extracted/Quantis"

if [ ! -d "${PROJECT_DIR}" ]; then
  echo "Error: Project directory ${PROJECT_DIR} not found."
  echo "Please ensure the project is extracted correctly."
  exit 1
fi

cd "${PROJECT_DIR}"
echo "Changed directory to $(pwd)"

# --- Backend API Setup (FastAPI/Python) ---
echo ""
echo "Setting up Quantis Backend API..."
API_DIR="${PROJECT_DIR}/api"

if [ ! -d "${API_DIR}" ]; then
    echo "Error: Backend API directory ${API_DIR} not found. Skipping API setup."
else
    cd "${API_DIR}"
    echo "Changed directory to $(pwd) for API setup."

    if [ ! -f "requirements.txt" ]; then
        echo "Error: requirements.txt not found in ${API_DIR}. Cannot install API dependencies."
    else
        echo "Creating Python virtual environment for API (venv_quantis_api_py)..."
        if ! python3.11 -m venv venv_quantis_api_py; then
            echo "Failed to create API virtual environment. Please check your Python installation."
        else
            source venv_quantis_api_py/bin/activate
            echo "API Python virtual environment created and activated."
            
            echo "Installing API Python dependencies from requirements.txt..."
            pip3 install -r requirements.txt
            echo "API dependencies installed."
            
            echo "To activate the API virtual environment later, run: source ${API_DIR}/venv_quantis_api_py/bin/activate"
            echo "To start the API server (from ${API_DIR} with venv activated): uvicorn app:app --reload (as per README)"
            deactivate
            echo "API Python virtual environment deactivated."
        fi
    fi
    cd "${PROJECT_DIR}" # Return to the main project directory
fi

# --- Web Frontend Setup (React/Node.js) ---
echo ""
echo "Setting up Quantis Web Frontend..."
# README structure shows frontend/, but package.json was found in web-frontend/
WEB_FRONTEND_DIR_QUANTIS="${PROJECT_DIR}/web-frontend"

if [ ! -d "${WEB_FRONTEND_DIR_QUANTIS}" ]; then
    # Fallback to frontend/ if web-frontend/ doesn't exist, as per README structure diagram
    if [ -d "${PROJECT_DIR}/frontend" ]; then
        WEB_FRONTEND_DIR_QUANTIS="${PROJECT_DIR}/frontend"
        echo "Note: Using ${WEB_FRONTEND_DIR_QUANTIS} as web-frontend directory was not found."
    else
        echo "Error: Web Frontend directory (neither ${PROJECT_DIR}/web-frontend nor ${PROJECT_DIR}/frontend) not found. Skipping Web Frontend setup."
        WEB_FRONTEND_DIR_QUANTIS=""
    fi
fi

if [ -n "${WEB_FRONTEND_DIR_QUANTIS}" ] && [ -d "${WEB_FRONTEND_DIR_QUANTIS}" ]; then
    cd "${WEB_FRONTEND_DIR_QUANTIS}"
    echo "Changed directory to $(pwd) for Web Frontend setup."

    if [ ! -f "package.json" ]; then
        echo "Error: package.json not found in ${WEB_FRONTEND_DIR_QUANTIS}. Cannot install Web Frontend dependencies."
    else
        echo "Installing Web Frontend Node.js dependencies using npm..."
        if ! command -v npm &> /dev/null; then echo "npm command not found."; else npm install; fi
        echo "Web Frontend dependencies installed."
        echo "To start the Web Frontend development server (from ${WEB_FRONTEND_DIR_QUANTIS}): npm start (as per package.json)"
        echo "To build the Web Frontend for production (from ${WEB_FRONTEND_DIR_QUANTIS}): npm run build (as per package.json)"
    fi
    cd "${PROJECT_DIR}" # Return to the main project directory
fi

# --- Mobile Frontend Setup (Next.js/Node.js) ---
echo ""
echo "Setting up Quantis Mobile Frontend..."
MOBILE_FRONTEND_DIR_QUANTIS="${PROJECT_DIR}/mobile-frontend"

if [ ! -d "${MOBILE_FRONTEND_DIR_QUANTIS}" ]; then
    echo "Error: Mobile Frontend directory ${MOBILE_FRONTEND_DIR_QUANTIS} not found. Skipping Mobile Frontend setup."
else
    cd "${MOBILE_FRONTEND_DIR_QUANTIS}"
    echo "Changed directory to $(pwd) for Mobile Frontend setup."

    if [ ! -f "package.json" ]; then
        echo "Error: package.json not found in ${MOBILE_FRONTEND_DIR_QUANTIS}. Cannot install Mobile Frontend dependencies."
    else
        echo "Installing Mobile Frontend Node.js dependencies using pnpm (as indicated by packageManager in package.json)..."
        if ! command -v pnpm &> /dev/null; then 
            echo "pnpm command not found. Attempting to install pnpm globally using npm..."
            if command -v npm &> /dev/null; then 
                sudo npm install -g pnpm
                if ! command -v pnpm &> /dev/null; then 
                    echo "Failed to install pnpm. Please install pnpm manually and re-run or install dependencies manually."
                else
                    echo "pnpm installed successfully. Proceeding with dependency installation."
                    pnpm install
                    echo "Mobile Frontend dependencies installed using pnpm."
                fi
            else 
                echo "npm command not found. Cannot install pnpm. Please install pnpm manually and re-run or install dependencies manually."
            fi
        else
            pnpm install
            echo "Mobile Frontend dependencies installed using pnpm."
        fi
        echo "To start the Mobile Frontend development server (from ${MOBILE_FRONTEND_DIR_QUANTIS}): pnpm dev (as per package.json)"
        echo "To build the Mobile Frontend for production (from ${MOBILE_FRONTEND_DIR_QUANTIS}): pnpm build (as per package.json)"
    fi
    cd "${PROJECT_DIR}" # Return to the main project directory
fi

# --- Models Setup (Python) ---
echo ""
echo "Setting up Quantis Models..."
MODELS_DIR_QUANTIS="${PROJECT_DIR}/models"

if [ ! -d "${MODELS_DIR_QUANTIS}" ]; then
    echo "Warning: Models directory ${MODELS_DIR_QUANTIS} not found. Skipping models setup."
else
    cd "${MODELS_DIR_QUANTIS}"
    echo "Changed directory to $(pwd) for models setup."
    # Check if there's a specific requirements.txt for models
    if [ -f "requirements.txt" ]; then
        echo "Found requirements.txt in ${MODELS_DIR_QUANTIS}. Consider setting up a separate Python environment for models or installing into the main API environment."
        echo "Example: pip3 install -r requirements.txt (ensure correct venv is active if desired)"
    elif [ -f "../api/requirements.txt" ]; then # Check if it uses the API's requirements
        echo "No specific requirements.txt in ${MODELS_DIR_QUANTIS}. It might use dependencies from the API's requirements.txt or have them listed in the main project requirements.txt (if one existed at root)."
    else
        echo "No requirements.txt found in ${MODELS_DIR_QUANTIS}. Dependencies for models might be part of the API or need manual identification."
    fi
    echo "Refer to README or specific scripts like 'train_model.py' in ${MODELS_DIR_QUANTIS} for instructions on training and using models."
    cd "${PROJECT_DIR}" # Return to the main project directory
fi

# --- Docker Compose (Optional) ---
echo ""
INFRA_DIR_QUANTIS="${PROJECT_DIR}/infrastructure"
if [ -f "${INFRA_DIR_QUANTIS}/docker-compose.yml" ]; then
    echo "Found docker-compose.yml in ${INFRA_DIR_QUANTIS}."
    echo "You can potentially run the application using Docker Compose:"
    echo "cd ${INFRA_DIR_QUANTIS} && docker-compose up -d"
    echo "Ensure Docker and Docker Compose are installed and configured."
elif [ -f "docker-compose.yml" ]; then # Check root as well
    echo "Found docker-compose.yml in the project root ${PROJECT_DIR}."
    echo "You can potentially run the application using Docker Compose:"
    echo "cd ${PROJECT_DIR} && docker-compose up -d"
    echo "Ensure Docker and Docker Compose are installed and configured."
fi

echo ""
echo "Quantis project setup script finished."
echo "Please ensure all prerequisites (Python, Node.js, npm, pnpm, Docker, Docker Compose if used) are installed."
echo "Review the project's README.md and the instructions above for running different components."
