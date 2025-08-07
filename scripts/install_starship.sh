#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starship Installer${NC}"
echo ""

# Check if starship is already installed
if command -v starship &> /dev/null; then
    echo -e "${GREEN}✅ Starship is already installed!${NC}"
    starship --version
else
    echo -e "${YELLOW}📦 Starship not found. Installing...${NC}"

    # Install starship
    curl -sS https://starship.rs/install.sh | sh
    
    if command -v starship &> /dev/null; then
        echo -e "${GREEN}✅ Starship installed successfully!${NC}"
        starship --version
    else
        echo -e "${RED}❌ Error installing Starship${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}🔧 Checking configuration...${NC}"

# Check if a starship config already exists
if [ -f ~/.config/starship.toml ]; then
    echo -e "${YELLOW}⚠️  Found existing configuration in ~/.config/starship.toml${NC}"
    echo -e "${YELLOW}   The configuration will be overwritten with stow${NC}"
fi

echo -e "${GREEN}✅ Script completed!${NC}"