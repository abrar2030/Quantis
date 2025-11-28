#!/bin/bash
# make_scripts_executable.sh - Make all automation scripts executable
#
# This script makes all the automation scripts in the directory executable.
#
# Author: Abrar Ahmed
# Date: May 22, 2025

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Making all automation scripts executable...${NC}"

# Find all .sh files in the current directory
SCRIPTS=$(find . -name "*.sh")

# Make each script executable
for script in $SCRIPTS; do
    chmod +x "$script"
    echo "Made executable: $script"
done

echo -e "${GREEN}All scripts are now executable!${NC}"
