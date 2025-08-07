#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🗑️  Starship Uninstaller${NC}"
echo ""

# Remove symlinks created by stow
echo -e "${YELLOW}🧹 Removing configuration...${NC}"
stow -D starship 2>/dev/null || echo "⚠️  No symlinks found"

# Ask if you want to remove the Starship program as well
read -p "🤔 Do you want to remove the Starship program as well? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}🗑️  Removing Starship program...${NC}"

    # Find where Starship is installed
    STARSHIP_PATH=$(which starship 2>/dev/null)
    if [ ! -z "$STARSHIP_PATH" ]; then
        sudo rm "$STARSHIP_PATH"
        echo -e "${GREEN}✅ Starship removed from $STARSHIP_PATH${NC}"
    else
        echo -e "${YELLOW}⚠️  Starship not found in PATH${NC}"
    fi
else
    echo -e "${GREEN}✅ Starship program kept${NC}"
fi

echo -e "${GREEN}✅ Starship cleanup completed!${NC}"