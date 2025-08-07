import logging
from pathlib import Path
from ..base import BaseInstaller

logger = logging.getLogger(__name__)

class StarshipInstaller(BaseInstaller):
    """Installer for the Starship prompt"""

    def __init__(self, package_name):
        super().__init__(package_name)
        self.binary_name = "starship"

    def install_software(self):
        """Install Starship using the official installation script"""
        logger.info("Installing Starship...")
        
        os_type = self._detect_os()
        
        if os_type in ["linux", "macos", "debian", "redhat", "arch"]:
            cmd = "curl -sS https://starship.rs/install.sh | sh -s -- --yes"
            result = self._run_command(cmd)
            
            if result.returncode == 0:
                logger.info("Starship installed successfully")
                return True
            else:
                logger.error(f"Starship installation failed: {result.stderr}")
                return False
        elif os_type == "windows":
            # TODO: Implement Windows installation
            logger.error(f"Unsupported OS: {os_type}")
        else:
            logger.error(f"Unsupported OS: {os_type}")
            return False
          
    def is_software_installed(self):
        """Check if Starship is installed"""
        return self._command_exists(self.binary_name)
    
    def uninstall_software(self):
        """Uninstall Starship"""
        logger.info("Uninstalling Starship...")
        
        # Starship doesn't have an official uninstaller
        # We need to remove the binary manually
        binary_path = self._find_starship_binary()
        
        if binary_path:
            try:
                binary_path.unlink()
                logger.info("Starship binary removed")
                return True
            except PermissionError:
                logger.error("Permission denied removing Starship binary")
                logger.info("💡 Try running with sudo/administrator privileges")
                return False
        else:
            logger.warning("Starship binary not found")
            return True
        
    def _find_starship_binary(self):
        """Find the Starship binary location."""
        import shutil
        binary_location = shutil.which(self.binary_name)
        
        if binary_location:
            return Path(binary_location)
        return None