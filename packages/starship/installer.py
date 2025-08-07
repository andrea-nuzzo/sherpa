import logging
from pathlib import Path
from ..base import BaseInstaller

logger = logging.getLogger(__name__)

class StarshipInstaller(BaseInstaller):
    """Installer for the Starship prompt"""

    def __init__(self, package_name):
        super().__init__(package_name)
        self.binary_name = "starship"
    
    # ==========================================
    # ABSTRACT METHODS - Software installation
    # ==========================================

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
    
    def is_software_installed(self):
        """Check if Starship is installed"""
        return self._command_exists(self.binary_name)    
    
    # ==========================================
    # INTEGRATION SETUP - Shell configuration
    # ==========================================
    
    def setup_integration(self):
        """Setup shell integration for starship prompt."""
        logger.info("Setting up shell integration...")
        
        current_shell = self._detect_current_shell()
        logger.debug(f"Detected shell: {current_shell}")
        
        if current_shell == "bash":
            return self._setup_bash_integration()
        elif current_shell == "zsh":
            return self._setup_zsh_integration()
        else:
            logger.warning(f"Unsupported shell for auto-config: {current_shell}")
            logger.info("💡 Manually add: eval \"$(starship init <your-shell>)\" to your shell config")
            return True  # Not a failure, just manual setup needed
     
    # ==========================================
    # PRIVATE METHODS - Helper functions
    # ==========================================   
    
    def _find_starship_binary(self):
        """Find the Starship binary location."""
        import shutil
        binary_location = shutil.which(self.binary_name)
        
        if binary_location:
            return Path(binary_location)
        return None
    
    def _detect_current_shell(self):
        """Detect current shell."""
        import os
        
        shell_path = os.environ.get('SHELL', '')
        if shell_path:
            shell_name = Path(shell_path).name
            if shell_name in ['bash', 'zsh', 'fish']:
                return shell_name
        
        # Fallback based on OS
        os_type = self._detect_os()
        if os_type in ['debian', 'redhat', 'arch', 'linux']:
            return 'bash'
        elif os_type == 'macos':
            return 'zsh'
        
        return 'unknown'
    
    def _setup_bash_integration(self):
        """Add starship to ~/.bashrc"""
        bashrc_path = self.home_dir / '.bashrc'
        starship_init = 'eval "$(starship init bash)"'
        
        try:
            # Check if already configured
            if bashrc_path.exists():
                content = bashrc_path.read_text()
                if starship_init in content:
                    logger.info("Bash integration already configured")
                    return True
            
            # Add to .bashrc
            with bashrc_path.open('a') as f:
                f.write(f'\n# Starship prompt\n{starship_init}\n')
            
            logger.info("Added starship to ~/.bashrc")
            logger.info("Run 'source ~/.bashrc' or open new terminal")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup bash integration: {e}")
            return False
    
    def _setup_zsh_integration(self):
        """Add starship to ~/.zshrc"""
        zshrc_path = self.home_dir / '.zshrc'
        starship_init = 'eval "$(starship init zsh)"'
        
        try:
            # Check if already configured
            if zshrc_path.exists():
                content = zshrc_path.read_text()
                if starship_init in content:
                    logger.info("Zsh integration already configured")
                    return True
            
            # Add to .zshrc
            with zshrc_path.open('a') as f:
                f.write(f'\n# Starship prompt\n{starship_init}\n')
            
            logger.info("Added starship to ~/.zshrc")
            logger.info("Run 'source ~/.zshrc' or open new terminal")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup zsh integration: {e}")
            return False