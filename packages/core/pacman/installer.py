import logging
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class PacmanInstaller(BaseInstaller):
    """Installer for Pacman package manager."""
    
    def install_software(self):
        """Pacman is pre-installed on Arch Linux systems."""
        logger.info("Checking Pacman installation...")
        
        if self.is_software_installed():
            logger.info("Pacman is already available")
            return True
        
        # Check if we're on an Arch-based system
        os_type = self._detect_os()
        if os_type != "arch":
            logger.error(f"Pacman is not supported on {os_type}")
            logger.info("Pacman is only available on Arch Linux-based systems")
            return False
        
        # Pacman should be pre-installed on Arch Linux
        logger.error("Pacman should be pre-installed on Arch Linux systems")
        logger.info("If Pacman is missing, your system installation may be incomplete")
        return False
    
    def uninstall_software(self):
        """Pacman cannot be safely uninstalled as it's a core system component."""
        logger.warning("Pacman is a core system component and cannot be safely uninstalled")
        logger.info("Uninstalling Pacman would break package management on Arch Linux systems")
        return False
    
    def is_software_installed(self):
        """Check if Pacman is available."""
        return self._command_exists("pacman")
    
    def update_package_database(self):
        """Update the Pacman package database."""
        logger.info("Updating Pacman package database...")
        
        if not self.is_software_installed():
            logger.error("Pacman is not available")
            return False
        
        try:
            result = self._run_command("sudo pacman -Sy")
            
            if result.returncode == 0:
                logger.info("Pacman package database updated successfully")
                return True
            else:
                logger.error(f"Failed to update Pacman package database: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update Pacman package database: {e}")
            return False
    
    def upgrade_packages(self):
        """Upgrade all installed packages using Pacman."""
        logger.info("Upgrading packages with Pacman...")
        
        if not self.is_software_installed():
            logger.error("Pacman is not available")
            return False
        
        try:
            # Update database and upgrade packages
            result = self._run_command("sudo pacman -Syu --noconfirm")
            
            if result.returncode == 0:
                logger.info("Packages upgraded successfully")
                return True
            else:
                logger.error(f"Failed to upgrade packages: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to upgrade packages: {e}")
            return False
    
    def install_aur_helper(self, helper="yay"):
        """Install an AUR helper like yay or paru."""
        logger.info(f"Installing AUR helper: {helper}")
        
        if not self.is_software_installed():
            logger.error("Pacman is not available")
            return False
        
        if self._command_exists(helper):
            logger.info(f"{helper} is already installed")
            return True
        
        try:
            # Install git and base-devel first (required for AUR)
            self._run_command("sudo pacman -S --noconfirm git base-devel")
            
            # Clone and build the AUR helper
            if helper == "yay":
                self._run_command("git clone https://aur.archlinux.org/yay.git /tmp/yay")
                self._run_command("cd /tmp/yay && makepkg -si --noconfirm")
            elif helper == "paru":
                self._run_command("git clone https://aur.archlinux.org/paru.git /tmp/paru")
                self._run_command("cd /tmp/paru && makepkg -si --noconfirm")
            else:
                logger.error(f"Unknown AUR helper: {helper}")
                return False
            
            if self._command_exists(helper):
                logger.info(f"{helper} installed successfully")
                return True
            else:
                logger.error(f"Failed to install {helper}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install AUR helper {helper}: {e}")
            return False