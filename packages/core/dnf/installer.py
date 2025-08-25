import logging
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class DnfInstaller(BaseInstaller):
    """Installer for DNF package manager."""
    
    def install_software(self):
        """DNF is typically pre-installed on Fedora and newer RHEL systems."""
        logger.info("Checking DNF installation...")
        
        if self.is_software_installed():
            logger.info("DNF is already available")
            return True
        
        # Check if we're on a Red Hat-based system
        os_type = self._detect_os()
        if os_type != "redhat":
            logger.error(f"DNF is not supported on {os_type}")
            logger.info("DNF is only available on Red Hat-based systems (Fedora, RHEL, CentOS, etc.)")
            return False
        
        # DNF should be pre-installed on modern Fedora/RHEL
        # If it's missing, try to install it using YUM (if available)
        if self._command_exists("yum"):
            logger.info("DNF not found, attempting to install using YUM...")
            try:
                result = self._run_command("sudo yum install -y dnf")
                
                if result.returncode == 0:
                    logger.info("DNF installed successfully using YUM")
                    return True
                else:
                    logger.error(f"Failed to install DNF: {result.stderr}")
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to install DNF: {e}")
                return False
        
        logger.error("DNF should be pre-installed on Fedora/RHEL systems")
        logger.info("If DNF is missing, your system installation may be incomplete")
        return False
    
    def uninstall_software(self):
        """DNF cannot be safely uninstalled as it's a core system component."""
        logger.warning("DNF is a core system component and cannot be safely uninstalled")
        logger.info("Uninstalling DNF would break package management on Fedora/RHEL systems")
        return False
    
    def is_software_installed(self):
        """Check if DNF is available."""
        return self._command_exists("dnf")
    
    def update_package_index(self):
        """Update the DNF package index."""
        logger.info("Updating DNF package cache...")
        
        if not self.is_software_installed():
            logger.error("DNF is not available")
            return False
        
        try:
            result = self._run_command("sudo dnf check-update")
            
            # DNF check-update returns 100 if updates are available, 0 if no updates
            if result.returncode in [0, 100]:
                logger.info("DNF package cache updated successfully")
                return True
            else:
                logger.error(f"Failed to update DNF package cache: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update DNF package cache: {e}")
            return False
    
    def upgrade_packages(self):
        """Upgrade all installed packages using DNF."""
        logger.info("Upgrading packages with DNF...")
        
        if not self.is_software_installed():
            logger.error("DNF is not available")
            return False
        
        try:
            result = self._run_command("sudo dnf upgrade -y")
            
            if result.returncode == 0:
                logger.info("Packages upgraded successfully")
                return True
            else:
                logger.error(f"Failed to upgrade packages: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to upgrade packages: {e}")
            return False