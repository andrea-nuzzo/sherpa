import logging
from pathlib import Path
from ..base import BaseInstaller

logger = logging.getLogger(__name__)

class TmuxInstaller(BaseInstaller):
    """Installer for tmux terminal multiplexer"""

    def __init__(self, package_name):
        super().__init__(package_name)
        self.binary_name = "tmux"
    
    def install_software(self):
        """Install tmux using system package manager"""
        logger.info("Installing tmux...")
        
        os_type = self._detect_os()
        package_manager, install_cmd = self._get_package_manager()
        
        if not package_manager:
            logger.error(f"No supported package manager found for OS: {os_type}")
            return False
        
        # Install tmux using the appropriate package manager
        full_command = f"{install_cmd} tmux"
        logger.info(f"Installing tmux using: {package_manager}")
        
        result = self._run_command(full_command)
        
        if result.returncode == 0:
            logger.info("tmux installed successfully")
            return True
        else:
            logger.error(f"tmux installation failed: {result.stderr}")
            return False
          
    def uninstall_software(self):
        """Uninstall tmux"""
        logger.info("Uninstalling tmux...")
        
        os_type = self._detect_os()
        package_manager, _ = self._get_package_manager()
        
        if not package_manager:
            logger.error(f"No supported package manager found for OS: {os_type}")
            return False
        
        # Uninstall commands for different package managers
        uninstall_commands = {
            "apt": "sudo apt remove -y tmux",
            "apt-get": "sudo apt-get remove -y tmux",
            "dnf": "sudo dnf remove -y tmux",
            "yum": "sudo yum remove -y tmux",
            "pacman": "sudo pacman -R --noconfirm tmux",
            "brew": "brew uninstall tmux",
            "winget": "winget uninstall tmux",
            "choco": "choco uninstall -y tmux"
        }
        
        uninstall_cmd = uninstall_commands.get(package_manager)
        if not uninstall_cmd:
            logger.error(f"Unsupported package manager for uninstall: {package_manager}")
            return False
        
        result = self._run_command(uninstall_cmd)
        
        if result.returncode == 0:
            logger.info("tmux uninstalled successfully")
            return True
        else:
            logger.error(f"tmux uninstall failed: {result.stderr}")
            return False
    
    def is_software_installed(self):
        """Check if tmux is installed"""
        return self._command_exists(self.binary_name)
    
    def setup_integration(self):
        """Setup tmux integration - no shell integration needed for tmux"""
        logger.info("No additional integration setup needed for tmux")
        return True
    
    def uninstall_integration(self):
        """Remove tmux integration - no shell integration to remove"""
        logger.info("No integration to remove for tmux")
        return True