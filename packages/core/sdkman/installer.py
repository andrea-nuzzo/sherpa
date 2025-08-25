import logging
import os
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class SdkmanInstaller(BaseInstaller):
    """Installer for SDKMAN! SDK manager."""
    
    def install_software(self):
        """Install SDKMAN! using the official installer."""
        logger.info("Installing SDKMAN!...")
        
        if self.is_software_installed():
            logger.info("SDKMAN! is already installed")
            return True
        
        try:
            # Use the official SDKMAN! installer
            install_cmd = 'curl -s "https://get.sdkman.io" | bash'
            result = self._run_command(install_cmd)
            
            if result.returncode == 0:
                logger.info("SDKMAN! installed successfully")
                self._setup_sdkman_shell_integration()
                return True
            else:
                logger.error(f"SDKMAN! installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install SDKMAN!: {e}")
            return False
    
    def uninstall_software(self):
        """Uninstall SDKMAN!."""
        logger.info("Uninstalling SDKMAN!...")
        
        if not self.is_software_installed():
            logger.info("SDKMAN! is not installed")
            return True
        
        try:
            # Remove SDKMAN! directory
            sdkman_dir = os.path.expanduser("~/.sdkman")
            if os.path.exists(sdkman_dir):
                self._run_command(f"rm -rf {sdkman_dir}")
            
            # Remove shell integration
            self._remove_sdkman_shell_integration()
            
            logger.info("SDKMAN! uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall SDKMAN!: {e}")
            return False
    
    def is_software_installed(self):
        """Check if SDKMAN! is installed."""
        sdkman_dir = os.path.expanduser("~/.sdkman")
        return os.path.exists(os.path.join(sdkman_dir, "bin", "sdkman-init.sh"))
    
    def _setup_sdkman_shell_integration(self):
        """Set up SDKMAN! shell integration."""
        logger.info("Setting up SDKMAN! shell integration...")
        
        # Shell integration code
        shell_integration = '''
# SDKMAN!
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$SDKMAN_DIR/bin/sdkman-init.sh" ]] && source "$SDKMAN_DIR/bin/sdkman-init.sh"
'''
        
        # Add to shell profiles
        try:
            for shell_file in ["~/.bashrc", "~/.zshrc", "~/.bash_profile"]:
                expanded_path = os.path.expanduser(shell_file)
                if os.path.exists(expanded_path):
                    with open(expanded_path, 'r') as f:
                        content = f.read()
                    if 'SDKMAN_DIR' not in content:
                        with open(expanded_path, 'a') as f:
                            f.write(shell_integration)
                        logger.debug(f"Added SDKMAN! integration to {shell_file}")
                        
        except Exception as e:
            logger.warning(f"Failed to set up shell integration: {e}")
    
    def _remove_sdkman_shell_integration(self):
        """Remove SDKMAN! shell integration."""
        logger.info("Removing SDKMAN! shell integration...")
        
        shell_files = ["~/.bashrc", "~/.zshrc", "~/.bash_profile"]
        
        for shell_file in shell_files:
            expanded_path = os.path.expanduser(shell_file)
            if os.path.exists(expanded_path):
                try:
                    # Remove SDKMAN!-related lines
                    self._run_command(f"sed -i.bak '/SDKMAN_DIR/d' {expanded_path}")
                    self._run_command(f"sed -i.bak '/sdkman-init.sh/d' {expanded_path}")
                    self._run_command(f"sed -i.bak '/# SDKMAN!/d' {expanded_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean {shell_file}: {e}")
    
    def list_available_sdks(self):
        """List available SDKs that can be installed via SDKMAN!."""
        logger.info("Listing available SDKs...")
        
        if not self.is_software_installed():
            logger.error("SDKMAN! is not available")
            return False
        
        try:
            result = self._run_command("source ~/.sdkman/bin/sdkman-init.sh && sdk list")
            
            if result.returncode == 0:
                logger.info("Available SDKs:")
                print(result.stdout)
                return True
            else:
                logger.error(f"Failed to list SDKs: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to list SDKs: {e}")
            return False