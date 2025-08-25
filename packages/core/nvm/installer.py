import logging
import os
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class NvmInstaller(BaseInstaller):
    """Installer for nvm Node Version Manager."""
    
    def install_software(self):
        """Install nvm using the official installer."""
        logger.info("Installing nvm...")
        
        if self.is_software_installed():
            logger.info("nvm is already installed")
            return True
        
        try:
            # Use the official nvm installer
            install_cmd = 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash'
            result = self._run_command(install_cmd)
            
            if result.returncode == 0:
                logger.info("nvm installed successfully")
                self._setup_nvm_shell_integration()
                return True
            else:
                logger.error(f"nvm installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install nvm: {e}")
            return False
    
    def uninstall_software(self):
        """Uninstall nvm."""
        logger.info("Uninstalling nvm...")
        
        if not self.is_software_installed():
            logger.info("nvm is not installed")
            return True
        
        try:
            # Remove nvm directory
            nvm_dir = os.path.expanduser("~/.nvm")
            if os.path.exists(nvm_dir):
                self._run_command(f"rm -rf {nvm_dir}")
            
            # Remove shell integration
            self._remove_nvm_shell_integration()
            
            logger.info("nvm uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall nvm: {e}")
            return False
    
    def is_software_installed(self):
        """Check if nvm is installed."""
        nvm_dir = os.path.expanduser("~/.nvm")
        return os.path.exists(os.path.join(nvm_dir, "nvm.sh"))
    
    def _setup_nvm_shell_integration(self):
        """Set up nvm shell integration."""
        logger.info("Setting up nvm shell integration...")
        
        # Shell integration code
        shell_integration = '''
# nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \\. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
'''
        
        # Add to shell profiles
        try:
            for shell_file in ["~/.bashrc", "~/.zshrc", "~/.bash_profile"]:
                expanded_path = os.path.expanduser(shell_file)
                if os.path.exists(expanded_path):
                    with open(expanded_path, 'r') as f:
                        content = f.read()
                    if 'NVM_DIR' not in content:
                        with open(expanded_path, 'a') as f:
                            f.write(shell_integration)
                        logger.debug(f"Added nvm integration to {shell_file}")
                        
        except Exception as e:
            logger.warning(f"Failed to set up shell integration: {e}")
    
    def _remove_nvm_shell_integration(self):
        """Remove nvm shell integration."""
        logger.info("Removing nvm shell integration...")
        
        shell_files = ["~/.bashrc", "~/.zshrc", "~/.bash_profile"]
        
        for shell_file in shell_files:
            expanded_path = os.path.expanduser(shell_file)
            if os.path.exists(expanded_path):
                try:
                    # Remove nvm-related lines
                    self._run_command(f"sed -i.bak '/NVM_DIR/d' {expanded_path}")
                    self._run_command(f"sed -i.bak '/nvm.sh/d' {expanded_path}")
                    self._run_command(f"sed -i.bak '/# nvm/d' {expanded_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean {shell_file}: {e}")