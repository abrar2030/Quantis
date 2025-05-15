#!/bin/bash

# Linting and Fixing Script for Quantis Project (Python, JavaScript, YAML)

set -e  # Exit immediately if a command exits with a non-zero status

echo "----------------------------------------"
echo "Starting linting and fixing process for Quantis..."
echo "----------------------------------------"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required tools
echo "Checking for required tools..."

# Check for Python
if ! command_exists python3; then
  echo "Error: python3 is required but not installed. Please install Python 3."
  exit 1
else
  echo "python3 is installed."
fi

# Check for pip
if ! command_exists pip3; then
  echo "Error: pip3 is required but not installed. Please install pip3."
  exit 1
else
  echo "pip3 is installed."
fi

# Check for Node.js and npm
if ! command_exists node; then
  echo "Error: node is required but not installed. Please install Node.js."
  exit 1
else
  echo "node is installed."
fi

if ! command_exists npm; then
  echo "Error: npm is required but not installed. Please install npm."
  exit 1
else
  echo "npm is installed."
fi

# Check for yamllint
if ! command_exists yamllint; then
  echo "Warning: yamllint is not installed. YAML validation will be limited."
  YAMLLINT_AVAILABLE=false
else
  echo "yamllint is installed."
  YAMLLINT_AVAILABLE=true
fi

# Install required Python linting tools if not already installed
echo "----------------------------------------"
echo "Installing/Updating Python linting tools..."
pip3 install --upgrade black isort flake8 pylint

# Install global npm packages for JavaScript/TypeScript linting
echo "----------------------------------------"
echo "Installing/Updating JavaScript linting tools..."
npm install -g eslint prettier

# Define directories to process
PYTHON_DIRECTORIES=(
  "api"
  "api/endpoints"
  "api/middleware"
  "data"
  "data/features"
  "models"
  "models/hyperparameter_tuning"
  "models/model_serving"
  "monitoring"
  "tests"
)

JS_DIRECTORIES=(
  "web-frontend/src"
  "web-frontend/src/components"
  "web-frontend/src/components/charts"
  "web-frontend/src/context"
  "web-frontend/src/pages"
  "mobile-frontend/src"
  "mobile-frontend/src/components"
  # Add other mobile-frontend subdirectories if they exist and need linting
)

YAML_DIRECTORIES=(
  "infrastructure"
  "infrastructure/kubernetes"
  "infrastructure/ansible"
  ".github/workflows"
  "monitoring"
)

# 1. Python Linting
echo "----------------------------------------"
echo "Running Python linting tools..."

# 1.1 Run Black (code formatter)
echo "Running Black code formatter..."
for dir in "${PYTHON_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Formatting Python files in $dir..."
    python3 -m black "$dir" || {
      echo "Black encountered issues in $dir. Please review the above errors."
    }
  else
    echo "Directory $dir not found. Skipping Black formatting for this directory."
  fi
done
echo "Black formatting completed."

# 1.2 Run isort (import sorter)
echo "Running isort to sort imports..."
for dir in "${PYTHON_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Sorting imports in Python files in $dir..."
    python3 -m isort "$dir" || {
      echo "isort encountered issues in $dir. Please review the above errors."
    }
  else
    echo "Directory $dir not found. Skipping isort for this directory."
  fi
done
echo "Import sorting completed."

# 1.3 Run flake8 (linter)
echo "Running flake8 linter..."
for dir in "${PYTHON_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Linting Python files in $dir with flake8..."
    python3 -m flake8 "$dir" || {
      echo "Flake8 found issues in $dir. Please review the above warnings/errors."
    }
  else
    echo "Directory $dir not found. Skipping flake8 for this directory."
  fi
done
echo "Flake8 linting completed."

# 1.4 Run pylint (more comprehensive linter)
echo "Running pylint for more comprehensive linting..."
for dir in "${PYTHON_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Linting Python files in $dir with pylint..."
    find "$dir" -type f -name "*.py" | xargs python3 -m pylint --disable=C0111,C0103,C0303,W0621,C0301,W0612,W0611,R0913,R0914,R0915 || {
      echo "Pylint found issues in $dir. Please review the above warnings/errors."
    }
  else
    echo "Directory $dir not found. Skipping pylint for this directory."
  fi
done
echo "Pylint linting completed."

# 2. JavaScript/TypeScript Linting
echo "----------------------------------------"
echo "Running JavaScript/TypeScript linting tools..."

# 2.1 Create ESLint config if it doesn't exist
if [ ! -f ".eslintrc.js" ]; then
  echo "Creating ESLint configuration..."
  cat > .eslintrc.js << 'EOF'
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: [
    'react',
  ],
  rules: {
    'no-unused-vars': 'warn',
    'react/prop-types': 'off',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
EOF
fi

# 2.2 Create Prettier config if it doesn't exist
if [ ! -f ".prettierrc.json" ]; then
  echo "Creating Prettier configuration..."
  cat > .prettierrc.json << 'EOF'
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
EOF
fi

# 2.3 Run ESLint
echo "Running ESLint for JavaScript/TypeScript files..."
for dir in "${JS_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Linting JavaScript/TypeScript files in $dir with ESLint..."
    npx eslint "$dir" --ext .js,.jsx,.ts,.tsx --fix || {
      echo "ESLint found issues in $dir. Please review the above warnings/errors."
    }
  else
    echo "Directory $dir not found. Skipping ESLint for this directory."
  fi
done
echo "ESLint linting completed."

# 2.4 Run Prettier
echo "Running Prettier for JavaScript/TypeScript files..."
for dir in "${JS_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Formatting JavaScript/TypeScript files in $dir with Prettier..."
    npx prettier --write "$dir/**/*.{js,jsx,ts,tsx}" || {
      echo "Prettier encountered issues in $dir. Please review the above errors."
    }
  else
    echo "Directory $dir not found. Skipping Prettier for this directory."
  fi
done
echo "Prettier formatting completed."

# 3. YAML Linting
echo "----------------------------------------"
echo "Running YAML linting tools..."

# 3.1 Run yamllint if available
if [ "$YAMLLINT_AVAILABLE" = true ]; then
  echo "Running yamllint for YAML files..."
  for dir in "${YAML_DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
      echo "Linting YAML files in $dir with yamllint..."
      yamllint "$dir" || {
        echo "yamllint found issues in $dir. Please review the above warnings/errors."
      }
    else
      # Check if it's a file directly in the root of a listed dir (like docker-compose.yml or prometheus.yml)
      if [ -f "$dir" ]; then
        echo "Linting YAML file $dir with yamllint..."
        yamllint "$dir" || {
          echo "yamllint found issues in $dir. Please review the above warnings/errors."
        }
      else
        echo "Directory/File $dir not found. Skipping yamllint for this path."
      fi
    fi
  done
  # Lint top-level YAML files if they exist
  if [ -f "infrastructure/docker-compose.yml" ]; then
      echo "Linting infrastructure/docker-compose.yml with yamllint..."
      yamllint "infrastructure/docker-compose.yml" || {
          echo "yamllint found issues in infrastructure/docker-compose.yml. Please review the above warnings/errors."
      }
  fi
  if [ -f "monitoring/prometheus.yml" ]; then
      echo "Linting monitoring/prometheus.yml with yamllint..."
      yamllint "monitoring/prometheus.yml" || {
          echo "yamllint found issues in monitoring/prometheus.yml. Please review the above warnings/errors."
      }
  fi
  echo "yamllint completed."
else
  echo "Skipping yamllint (not installed)."
  
  # 3.2 Basic YAML validation using Python
  echo "Performing basic YAML validation using Python..."
  pip3 install --upgrade pyyaml
  
  YAML_FILES_TO_VALIDATE=()
  for dir in "${YAML_DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
      while IFS= read -r -d $'\0' file; do
        YAML_FILES_TO_VALIDATE+=("$file")
      done < <(find "$dir" -type f \( -name "*.yaml" -o -name "*.yml" \) -print0)
    elif [ -f "$dir" ]; then
       YAML_FILES_TO_VALIDATE+=("$dir")
    fi
  done
  # Add top-level files explicitly if they exist
  if [ -f "infrastructure/docker-compose.yml" ]; then
      YAML_FILES_TO_VALIDATE+=("infrastructure/docker-compose.yml")
  fi
  if [ -f "monitoring/prometheus.yml" ]; then
      YAML_FILES_TO_VALIDATE+=("monitoring/prometheus.yml")
  fi

  echo "Validating YAML files..."
  for file in "${YAML_FILES_TO_VALIDATE[@]}"; do
      echo "Validating $file..."
      python3 -c "import yaml; yaml.safe_load(open('$file', 'r'))" || {
          echo "YAML validation found issues in $file. Please review the above errors."
      }
  done
  echo "Basic YAML validation completed."
fi

# 4. Common Fixes for All File Types
echo "----------------------------------------"
echo "Applying common fixes to all file types..."

# 4.1 Fix trailing whitespace
echo "Fixing trailing whitespace..."
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.yaml" -o -name "*.yml" \) -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/dist/*" -exec sed -i 's/[ \t]*$//' {} \;
echo "Fixed trailing whitespace."

# 4.2 Ensure newline at end of file
echo "Ensuring newline at end of files..."
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.yaml" -o -name "*.yml" \) -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/dist/*" -exec sh -c '[ -n "$(tail -c1 "$1")" ] && echo "" >> "$1"' sh {} \;
echo "Ensured newline at end of files."

echo "----------------------------------------"
echo "Linting and fixing process for Quantis completed!"
echo "----------------------------------------"
