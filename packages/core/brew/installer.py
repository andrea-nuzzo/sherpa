import logging
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class BrewInstaller(BaseInstaller):
    """Installer for Homebrew package manager."""
    
    def install_software(self):
        """Install Homebrew using the official install script."""
        logger.info("Installing Homebrew...")
        
        if self.is_software_installed():
            logger.info("Homebrew is already installed")
            return True
        
        # Check OS support
        os_type = self._detect_os()
        if os_type not in ["macos", "linux"]:
            logger.error(f"Homebrew is not supported on {os_type}")
            return False
        
        try:
            # Use the official Homebrew installation script
            install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            result = self._run_command(install_cmd)
            
            if result.returncode == 0:
                logger.info("Homebrew installed successfully")
                # Add brew to PATH if needed (the install script usually does this)
                self._setup_brew_path()
                return True
            else:
                logger.error(f"Homebrew installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install Homebrew: {e}")
            return False
    
    def uninstall_software(self):
        """Uninstall Homebrew using the official uninstall script."""
        logger.info("Uninstalling Homebrew...")
        
        if not self.is_software_installed():
            logger.info("Homebrew is not installed")
            return True
        
        try:
            # Use the official Homebrew uninstallation script
            uninstall_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)"'
            result = self._run_command(uninstall_cmd)
            
            if result.returncode == 0:
                logger.info("Homebrew uninstalled successfully")
                return True
            else:
                logger.error(f"Homebrew uninstallation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to uninstall Homebrew: {e}")
            return False
    
    def is_software_installed(self):
        """Check if Homebrew is installed by looking for the brew command."""
        return self._command_exists("brew")
    
    def _setup_brew_path(self):
        """Ensure brew is in PATH by checking common locations."""
        import platform
        
        # Common Homebrew paths
        if platform.system().lower() == "darwin":  # macOS
            if platform.machine().lower() in ["arm64", "aarch64"]:
                # Apple Silicon
                brew_path = "/opt/homebrew/bin/brew"
            else:
                # Intel
                brew_path = "/usr/local/bin/brew"
        else:  # Linux
            brew_path = "/home/linuxbrew/.linuxbrew/bin/brew"
        
        # Check if brew exists at expected location
        from pathlib import Path
        if Path(brew_path).exists():
            logger.debug(f"Homebrew found at: {brew_path}")
            # The install script should have already set up PATH
            return True
        
        return self._command_exists("brew")