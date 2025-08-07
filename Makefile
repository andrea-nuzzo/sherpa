# Dotfiles Makefile
.PHONY: help starship all

# Target di default
help:
	@echo "🚀 Dotfiles Manager"
	@echo ""
	@echo "Available commands:"
	@echo "make starship  - Install and Configure Starship"


# Install and Configure Starship
starship:
	@echo "📦 Installing Starship..."
	@./scripts/install_starship.sh
	@stow starship
	@echo "✨ Starship installed and configured successfully"

# Install all
all: starship
	@echo "All tasks completed successfully"