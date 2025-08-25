import logging
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class AptInstaller(BaseInstaller):
    """Installer for APT package manager."""
    
    def install_software(self):
        """APT is typically pre-installed on Debian/Ubuntu systems."""
        logger.info("Checking APT installation...")
        
        if self.is_software_installed():
            logger.info("APT is already available")
            return True
        
        # Check if we're on a Debian-based system
        os_type = self._detect_os()
        if os_type != "debian":
            logger.error(f"APT is not supported on {os_type}")
            logger.info("APT is only available on Debian-based systems (Ubuntu, Debian, etc.)")
            return False
        
        # APT should be pre-installed on Debian/Ubuntu
        # If it's missing, the system might be broken
        logger.error("APT should be pre-installed on Debian/Ubuntu systems")
        logger.info("If APT is missing, your system installation may be incomplete")
        return False
    
    def uninstall_software(self):
        """APT cannot be safely uninstalled as it's a core system component."""
        logger.warning("APT is a core system component and cannot be safely uninstalled")
        logger.info("Uninstalling APT would break package management on Debian/Ubuntu systems")
        return False
    
    def is_software_installed(self):
        """Check if APT is available."""
        return self._command_exists("apt") and self._command_exists("apt-get")
    
    def update_package_index(self):
        """Update the APT package index."""
        logger.info("Updating APT package index...")
        
        if not self.is_software_installed():
            logger.error("APT is not available")
            return False
        
        try:
            result = self._run_command("sudo apt update")
            
            if result.returncode == 0:
                logger.info("APT package index updated successfully")
                return True
            else:
                logger.error(f"Failed to update APT package index: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update APT package index: {e}")
            return False
    
    def upgrade_packages(self):
        """Upgrade all installed packages using APT."""
        logger.info("Upgrading packages with APT...")
        
        if not self.is_software_installed():
            logger.error("APT is not available")
            return False
        
        try:
            # First update the package index
            if not self.update_package_index():
                return False
            
            # Then upgrade packages
            result = self._run_command("sudo apt upgrade -y")
            
            if result.returncode == 0:
                logger.info("Packages upgraded successfully")
                return True
            else:
                logger.error(f"Failed to upgrade packages: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to upgrade packages: {e}")
            return False