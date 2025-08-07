# Dotfiles Makefile
.PHONY: help starship all

# Target di default
help:
	@echo "🚀 Dotfiles Manager"
	@echo ""
	@echo "📦 INSTALL:"
	@echo "make starship  - Install and Configure Starship"
	@echo "make all       - Install all components"
	@echo ""
	@echo "🧹 CLEANUP:"
	@echo "make uninstall-starship - Uninstall Starship and remove symlinks"
	@echo "make clean     - Remove all symlinks (maintain components)"
	@echo "make clean-all - Remove all symlinks and components"



starship:
	@echo "📦 Installing Starship..."
	@./scripts/install_starship.sh
	@stow starship
	@echo "✨ Starship installed and configured successfully"

uninstall-starship:
	@echo "🗑️ Uninstalling Starship..."
	@./scripts/uninstall_starship.sh
	@echo "✅ Starship uninstalled successfully"

all: starship
	@echo "All tasks completed successfully"

clean-all:
	@echo "🔥 Resetting all symlinks and components..."
	@./scripts/uninstall_all.sh

clean:
	@echo "🧹 Cleaning up symlinks..."
	@stow -D */ 2>/dev/null || echo "⚠️ No symlinks to remove"
	@echo "All configuration files removed"