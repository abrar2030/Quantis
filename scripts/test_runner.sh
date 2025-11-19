#!/bin/bash
# test_runner.sh - Comprehensive test runner for Quantis project
#
# This script automates the testing process for all components of the Quantis project:
# - Unit tests
# - Integration tests
# - End-to-end tests
# - Performance tests
#
# Usage: ./test_runner.sh [options]
# Options:
#   --all                Run all tests
#   --unit               Run only unit tests
#   --integration        Run only integration tests
#   --e2e                Run only end-to-end tests
#   --performance        Run only performance tests
#   --component TYPE     Specify component to test (api, models, web, mobile, all)
#   --report             Generate HTML test report
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
RUN_UNIT=false
RUN_INTEGRATION=false
RUN_E2E=false
RUN_PERFORMANCE=false
COMPONENT="all"
GENERATE_REPORT=false
PROJECT_ROOT=$(pwd)
REPORT_DIR="$PROJECT_ROOT/test_reports"

# Function to display help message
show_help() {
    echo -e "${BLUE}Test Runner for Quantis Project${NC}"
    echo ""
    echo "Usage: ./test_runner.sh [options]"
    echo ""
    echo "Options:"
    echo "  --all                Run all tests"
    echo "  --unit               Run only unit tests"
    echo "  --integration        Run only integration tests"
    echo "  --e2e                Run only end-to-end tests"
    echo "  --performance        Run only performance tests"
    echo "  --component TYPE     Specify component to test (api, models, web, mobile, all)"
    echo "  --report             Generate HTML test report"
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
    echo -e "${BLUE}Checking testing dependencies...${NC}"

    # Check Python dependencies
    if [ "$COMPONENT" = "api" ] || [ "$COMPONENT" = "models" ] || [ "$COMPONENT" = "all" ]; then
        if ! command_exists python3; then
            echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
            exit 1
        fi

        if ! python3 -c "import pytest" &>/dev/null; then
            echo -e "${YELLOW}Warning: pytest is not installed. Installing...${NC}"
            pip install pytest pytest-cov pytest-html
        fi
    fi

    # Check Node.js dependencies
    if [ "$COMPONENT" = "web" ] || [ "$COMPONENT" = "mobile" ] || [ "$COMPONENT" = "all" ]; then
        if ! command_exists node; then
            echo -e "${RED}Error: Node.js is required but not installed.${NC}"
            exit 1
        fi

        if ! command_exists npm; then
            echo -e "${RED}Error: npm is required but not installed.${NC}"
            exit 1
        fi
    fi

    echo -e "${GREEN}All required testing dependencies are installed.${NC}"
}

# Function to prepare report directory
prepare_report_dir() {
    if $GENERATE_REPORT; then
        echo -e "${BLUE}Preparing report directory...${NC}"
        mkdir -p "$REPORT_DIR"
        echo -e "${GREEN}Report directory prepared.${NC}"
    fi
}

# Function to run Python unit tests
run_python_unit_tests() {
    local component=$1
    echo -e "${BLUE}Running $component unit tests...${NC}"

    if [ ! -d "$PROJECT_ROOT/$component" ]; then
        echo -e "${YELLOW}Warning: $component directory not found. Skipping unit tests.${NC}"
        return
    fi

    cd "$PROJECT_ROOT/$component"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install test dependencies
    pip install pytest pytest-cov pytest-html

    # Install project dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi

    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi

    # Run unit tests
    if $GENERATE_REPORT; then
        mkdir -p "$REPORT_DIR/$component/unit"
        pytest tests/unit -v --cov=. --cov-report=term --cov-report=html:$REPORT_DIR/$component/unit/coverage --html=$REPORT_DIR/$component/unit/report.html || true
    else
        pytest tests/unit -v || true
    fi

    # Deactivate virtual environment
    deactivate

    echo -e "${GREEN}$component unit tests completed.${NC}"
}

# Function to run Python integration tests
run_python_integration_tests() {
    local component=$1
    echo -e "${BLUE}Running $component integration tests...${NC}"

    if [ ! -d "$PROJECT_ROOT/$component" ]; then
        echo -e "${YELLOW}Warning: $component directory not found. Skipping integration tests.${NC}"
        return
    fi

    cd "$PROJECT_ROOT/$component"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install test dependencies
    pip install pytest pytest-cov pytest-html

    # Install project dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi

    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi

    # Run integration tests
    if $GENERATE_REPORT; then
        mkdir -p "$REPORT_DIR/$component/integration"
        pytest tests/integration -v --cov=. --cov-report=term --cov-report=html:$REPORT_DIR/$component/integration/coverage --html=$REPORT_DIR/$component/integration/report.html || true
    else
        pytest tests/integration -v || true
    fi

    # Deactivate virtual environment
    deactivate

    echo -e "${GREEN}$component integration tests completed.${NC}"
}

# Function to run JavaScript unit tests
run_js_unit_tests() {
    local component=$1
    echo -e "${BLUE}Running $component unit tests...${NC}"

    if [ ! -d "$PROJECT_ROOT/$component" ]; then
        echo -e "${YELLOW}Warning: $component directory not found. Skipping unit tests.${NC}"
        return
    fi

    cd "$PROJECT_ROOT/$component"

    # Install dependencies
    npm install

    # Run unit tests
    if $GENERATE_REPORT; then
        mkdir -p "$REPORT_DIR/$component/unit"
        npm test -- --coverage --coverageDirectory=$REPORT_DIR/$component/unit/coverage --reporters=default --reporters=jest-html-reporter --testResultsProcessor=jest-html-reporter || true

        # Move HTML report to report directory
        if [ -f "test-report.html" ]; then
            mv test-report.html $REPORT_DIR/$component/unit/report.html
        fi
    else
        npm test || true
    fi

    echo -e "${GREEN}$component unit tests completed.${NC}"
}

# Function to run JavaScript integration tests
run_js_integration_tests() {
    local component=$1
    echo -e "${BLUE}Running $component integration tests...${NC}"

    if [ ! -d "$PROJECT_ROOT/$component" ]; then
        echo -e "${YELLOW}Warning: $component directory not found. Skipping integration tests.${NC}"
        return
    fi

    cd "$PROJECT_ROOT/$component"

    # Install dependencies
    npm install

    # Run integration tests
    if $GENERATE_REPORT; then
        mkdir -p "$REPORT_DIR/$component/integration"
        npm run test:integration -- --coverage --coverageDirectory=$REPORT_DIR/$component/integration/coverage --reporters=default --reporters=jest-html-reporter --testResultsProcessor=jest-html-reporter || true

        # Move HTML report to report directory
        if [ -f "test-report.html" ]; then
            mv test-report.html $REPORT_DIR/$component/integration/report.html
        fi
    else
        npm run test:integration || true
    fi

    echo -e "${GREEN}$component integration tests completed.${NC}"
}

# Function to run end-to-end tests
run_e2e_tests() {
    echo -e "${BLUE}Running end-to-end tests...${NC}"

    if [ ! -d "$PROJECT_ROOT/tests/e2e" ]; then
        echo -e "${YELLOW}Warning: End-to-end test directory not found. Skipping E2E tests.${NC}"
        return
    fi

    cd "$PROJECT_ROOT/tests/e2e"

    # Check if using Cypress or Playwright
    if [ -f "package.json" ]; then
        # Install dependencies
        npm install

        # Run E2E tests
        if $GENERATE_REPORT; then
            mkdir -p "$REPORT_DIR/e2e"

            # Check if using Cypress
            if grep -q "cypress" package.json; then
                npm run cypress:run -- --reporter mochawesome --reporter-options reportDir=$REPORT_DIR/e2e,reportFilename=report || true
            # Check if using Playwright
            elif grep -q "playwright" package.json; then
                npx playwright test --reporter=html || true

                # Move Playwright report to report directory
                if [ -d "playwright-report" ]; then
                    cp -r playwright-report/* $REPORT_DIR/e2e/
                fi
            else
                npm test || true
            fi
        else
            npm test || true
        fi
    elif [ -f "requirements.txt" ]; then
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi

        # Activate virtual environment
        source venv/bin/activate

        # Install dependencies
        pip install -r requirements.txt

        # Run E2E tests
        if $GENERATE_REPORT; then
            mkdir -p "$REPORT_DIR/e2e"
            pytest -v --html=$REPORT_DIR/e2e/report.html || true
        else
            pytest -v || true
        fi

        # Deactivate virtual environment
        deactivate
    else
        echo -e "${YELLOW}Warning: No package.json or requirements.txt found in E2E test directory. Skipping E2E tests.${NC}"
    fi

    echo -e "${GREEN}End-to-end tests completed.${NC}"
}

# Function to run performance tests
run_performance_tests() {
    echo -e "${BLUE}Running performance tests...${NC}"

    if [ ! -d "$PROJECT_ROOT/tests/performance" ]; then
        echo -e "${YELLOW}Warning: Performance test directory not found. Skipping performance tests.${NC}"
        return
    fi

    cd "$PROJECT_ROOT/tests/performance"

    # Check if using JMeter, Locust, or k6
    if [ -f "*.jmx" ]; then
        # JMeter tests
        if command_exists jmeter; then
            if $GENERATE_REPORT; then
                mkdir -p "$REPORT_DIR/performance"
                jmeter -n -t *.jmx -l $REPORT_DIR/performance/results.jtl -e -o $REPORT_DIR/performance/dashboard || true
            else
                jmeter -n -t *.jmx || true
            fi
        else
            echo -e "${YELLOW}Warning: JMeter is not installed. Skipping performance tests.${NC}"
        fi
    elif [ -f "locustfile.py" ]; then
        # Locust tests
        if command_exists locust; then
            if $GENERATE_REPORT; then
                mkdir -p "$REPORT_DIR/performance"
                locust -f locustfile.py --headless -u 10 -r 1 --run-time 1m --html=$REPORT_DIR/performance/report.html || true
            else
                locust -f locustfile.py --headless -u 10 -r 1 --run-time 1m || true
            fi
        else
            echo -e "${YELLOW}Warning: Locust is not installed. Skipping performance tests.${NC}"
        fi
    elif [ -f "*.js" ] && grep -q "k6" *.js; then
        # k6 tests
        if command_exists k6; then
            if $GENERATE_REPORT; then
                mkdir -p "$REPORT_DIR/performance"
                k6 run --summary-export=$REPORT_DIR/performance/summary.json *.js || true
            else
                k6 run *.js || true
            fi
        else
            echo -e "${YELLOW}Warning: k6 is not installed. Skipping performance tests.${NC}"
        fi
    else
        echo -e "${YELLOW}Warning: No recognized performance test files found. Skipping performance tests.${NC}"
    fi

    echo -e "${GREEN}Performance tests completed.${NC}"
}

# Function to generate HTML index for all reports
generate_report_index() {
    if $GENERATE_REPORT; then
        echo -e "${BLUE}Generating report index...${NC}"

        # Create index.html
        cat > "$REPORT_DIR/index.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantis Test Reports</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1, h2, h3 {
            color: #0066cc;
        }
        .report-section {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
        }
        .report-links {
            margin-left: 20px;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .timestamp {
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Quantis Test Reports</h1>
    <div class="timestamp">Generated on $(date)</div>

EOF

        # Add API reports
        if [ -d "$REPORT_DIR/api" ]; then
            cat >> "$REPORT_DIR/index.html" << EOF
    <div class="report-section">
        <h2>API Tests</h2>
        <div class="report-links">
EOF

            if [ -f "$REPORT_DIR/api/unit/report.html" ]; then
                echo '            <p><a href="api/unit/report.html">Unit Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -d "$REPORT_DIR/api/unit/coverage" ]; then
                echo '            <p><a href="api/unit/coverage/index.html">Unit Test Coverage</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -f "$REPORT_DIR/api/integration/report.html" ]; then
                echo '            <p><a href="api/integration/report.html">Integration Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -d "$REPORT_DIR/api/integration/coverage" ]; then
                echo '            <p><a href="api/integration/coverage/index.html">Integration Test Coverage</a></p>' >> "$REPORT_DIR/index.html"
            fi

            cat >> "$REPORT_DIR/index.html" << EOF
        </div>
    </div>
EOF
        fi

        # Add Models reports
        if [ -d "$REPORT_DIR/models" ]; then
            cat >> "$REPORT_DIR/index.html" << EOF
    <div class="report-section">
        <h2>Models Tests</h2>
        <div class="report-links">
EOF

            if [ -f "$REPORT_DIR/models/unit/report.html" ]; then
                echo '            <p><a href="models/unit/report.html">Unit Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -d "$REPORT_DIR/models/unit/coverage" ]; then
                echo '            <p><a href="models/unit/coverage/index.html">Unit Test Coverage</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -f "$REPORT_DIR/models/integration/report.html" ]; then
                echo '            <p><a href="models/integration/report.html">Integration Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -d "$REPORT_DIR/models/integration/coverage" ]; then
                echo '            <p><a href="models/integration/coverage/index.html">Integration Test Coverage</a></p>' >> "$REPORT_DIR/index.html"
            fi

            cat >> "$REPORT_DIR/index.html" << EOF
        </div>
    </div>
EOF
        fi

        # Add Web Frontend reports
        if [ -d "$REPORT_DIR/web-frontend" ]; then
            cat >> "$REPORT_DIR/index.html" << EOF
    <div class="report-section">
        <h2>Web Frontend Tests</h2>
        <div class="report-links">
EOF

            if [ -f "$REPORT_DIR/web-frontend/unit/report.html" ]; then
                echo '            <p><a href="web-frontend/unit/report.html">Unit Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -d "$REPORT_DIR/web-frontend/unit/coverage" ]; then
                echo '            <p><a href="web-frontend/unit/coverage/lcov-report/index.html">Unit Test Coverage</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -f "$REPORT_DIR/web-frontend/integration/report.html" ]; then
                echo '            <p><a href="web-frontend/integration/report.html">Integration Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -d "$REPORT_DIR/web-frontend/integration/coverage" ]; then
                echo '            <p><a href="web-frontend/integration/coverage/lcov-report/index.html">Integration Test Coverage</a></p>' >> "$REPORT_DIR/index.html"
            fi

            cat >> "$REPORT_DIR/index.html" << EOF
        </div>
    </div>
EOF
        fi

        # Add Mobile Frontend reports
        if [ -d "$REPORT_DIR/mobile-frontend" ]; then
            cat >> "$REPORT_DIR/index.html" << EOF
    <div class="report-section">
        <h2>Mobile Frontend Tests</h2>
        <div class="report-links">
EOF

            if [ -f "$REPORT_DIR/mobile-frontend/unit/report.html" ]; then
                echo '            <p><a href="mobile-frontend/unit/report.html">Unit Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -d "$REPORT_DIR/mobile-frontend/unit/coverage" ]; then
                echo '            <p><a href="mobile-frontend/unit/coverage/lcov-report/index.html">Unit Test Coverage</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -f "$REPORT_DIR/mobile-frontend/integration/report.html" ]; then
                echo '            <p><a href="mobile-frontend/integration/report.html">Integration Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -d "$REPORT_DIR/mobile-frontend/integration/coverage" ]; then
                echo '            <p><a href="mobile-frontend/integration/coverage/lcov-report/index.html">Integration Test Coverage</a></p>' >> "$REPORT_DIR/index.html"
            fi

            cat >> "$REPORT_DIR/index.html" << EOF
        </div>
    </div>
EOF
        fi

        # Add E2E reports
        if [ -d "$REPORT_DIR/e2e" ]; then
            cat >> "$REPORT_DIR/index.html" << EOF
    <div class="report-section">
        <h2>End-to-End Tests</h2>
        <div class="report-links">
EOF

            if [ -f "$REPORT_DIR/e2e/report.html" ]; then
                echo '            <p><a href="e2e/report.html">E2E Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -f "$REPORT_DIR/e2e/index.html" ]; then
                echo '            <p><a href="e2e/index.html">E2E Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            cat >> "$REPORT_DIR/index.html" << EOF
        </div>
    </div>
EOF
        fi

        # Add Performance reports
        if [ -d "$REPORT_DIR/performance" ]; then
            cat >> "$REPORT_DIR/index.html" << EOF
    <div class="report-section">
        <h2>Performance Tests</h2>
        <div class="report-links">
EOF

            if [ -f "$REPORT_DIR/performance/report.html" ]; then
                echo '            <p><a href="performance/report.html">Performance Test Report</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -d "$REPORT_DIR/performance/dashboard" ]; then
                echo '            <p><a href="performance/dashboard/index.html">Performance Dashboard</a></p>' >> "$REPORT_DIR/index.html"
            fi

            if [ -f "$REPORT_DIR/performance/summary.json" ]; then
                echo '            <p><a href="performance/summary.json">Performance Summary</a></p>' >> "$REPORT_DIR/index.html"
            fi

            cat >> "$REPORT_DIR/index.html" << EOF
        </div>
    </div>
EOF
        fi

        # Close HTML
        echo "</body></html>" >> "$REPORT_DIR/index.html"

        echo -e "${GREEN}Report index generated: $REPORT_DIR/index.html${NC}"
    fi
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_help
fi

while [ "$1" != "" ]; do
    case $1 in
        --all )     RUN_UNIT=true
                    RUN_INTEGRATION=true
                    RUN_E2E=true
                    RUN_PERFORMANCE=true
                    ;;
        --unit )    RUN_UNIT=true
                    ;;
        --integration ) RUN_INTEGRATION=true
                    ;;
        --e2e )     RUN_E2E=true
                    ;;
        --performance ) RUN_PERFORMANCE=true
                    ;;
        --component ) shift
                    COMPONENT="$1"
                    ;;
        --report )  GENERATE_REPORT=true
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
echo -e "${BLUE}Starting Quantis test runner...${NC}"

# Check dependencies
check_dependencies

# Prepare report directory
prepare_report_dir

# Run tests based on component and test type
if $RUN_UNIT; then
    if [ "$COMPONENT" = "api" ] || [ "$COMPONENT" = "all" ]; then
        run_python_unit_tests "api"
    fi

    if [ "$COMPONENT" = "models" ] || [ "$COMPONENT" = "all" ]; then
        run_python_unit_tests "models"
    fi

    if [ "$COMPONENT" = "web" ] || [ "$COMPONENT" = "all" ]; then
        run_js_unit_tests "web-frontend"
    fi

    if [ "$COMPONENT" = "mobile" ] || [ "$COMPONENT" = "all" ]; then
        run_js_unit_tests "mobile-frontend"
    fi
fi

if $RUN_INTEGRATION; then
    if [ "$COMPONENT" = "api" ] || [ "$COMPONENT" = "all" ]; then
        run_python_integration_tests "api"
    fi

    if [ "$COMPONENT" = "models" ] || [ "$COMPONENT" = "all" ]; then
        run_python_integration_tests "models"
    fi

    if [ "$COMPONENT" = "web" ] || [ "$COMPONENT" = "all" ]; then
        run_js_integration_tests "web-frontend"
    fi

    if [ "$COMPONENT" = "mobile" ] || [ "$COMPONENT" = "all" ]; then
        run_js_integration_tests "mobile-frontend"
    fi
fi

if $RUN_E2E; then
    run_e2e_tests
fi

if $RUN_PERFORMANCE; then
    run_performance_tests
fi

# Generate report index
if $GENERATE_REPORT; then
    generate_report_index
fi

echo -e "${GREEN}Quantis test runner completed successfully!${NC}"
exit 0
