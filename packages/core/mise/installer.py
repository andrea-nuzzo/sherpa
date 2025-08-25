import logging
import os
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class MiseInstaller(BaseInstaller):
    """Installer for mise (polyglot runtime manager)."""
    
    def install_software(self):
        """Install mise using the official installer."""
        logger.info("Installing mise...")
        
        if self.is_software_installed():
            logger.info("mise is already installed")
            return True
        
        try:
            # Use the official mise installation script
            install_cmd = 'curl https://mise.jdx.dev/install.sh | sh'
            result = self._run_command(install_cmd)
            
            if result.returncode == 0:
                logger.info("mise installed successfully")
                self._setup_mise_shell_integration()
                return True
            else:
                logger.error(f"mise installation failed: {result.stderr}")
                # Try alternative installation via package manager
                return self._install_via_package_manager()
                
        except Exception as e:
            logger.error(f"Failed to install mise: {e}")
            return self._install_via_package_manager()
    
    def _install_via_package_manager(self):
        """Install mise via system package manager as fallback."""
        logger.info("Trying to install mise via package manager...")
        
        package_manager, install_cmd = self._get_package_manager()
        if not package_manager:
            logger.error("No package manager available")
            return False
        
        try:
            if package_manager == "brew":
                result = self._run_command("brew install mise")
            elif package_manager == "apt":
                # Add mise repository first
                self._run_command("curl -fsSL https://mise.jdx.dev/gpg-key.pub | sudo gpg --dearmor -o /etc/apt/keyrings/mise-archive-keyring.gpg")
                self._run_command('echo "deb [signed-by=/etc/apt/keyrings/mise-archive-keyring.gpg arch=amd64] https://mise.jdx.dev/deb stable main" | sudo tee /etc/apt/sources.list.d/mise.list')
                self._run_command("sudo apt update")
                result = self._run_command("sudo apt install -y mise")
            else:
                logger.warning(f"Package manager {package_manager} not supported for mise")
                return False
            
            if result.returncode == 0:
                logger.info("mise installed successfully via package manager")
                self._setup_mise_shell_integration()
                return True
            else:
                logger.error(f"Failed to install mise via package manager: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install mise via package manager: {e}")
            return False
    
    def uninstall_software(self):
        """Uninstall mise."""
        logger.info("Uninstalling mise...")
        
        if not self.is_software_installed():
            logger.info("mise is not installed")
            return True
        
        try:
            # Try to uninstall via the same method it was installed
            package_manager, _ = self._get_package_manager()
            
            if package_manager == "brew" and self._command_exists("brew"):
                result = self._run_command("brew uninstall mise")
            elif package_manager in ["apt", "apt-get"] and self._command_exists("apt"):
                result = self._run_command("sudo apt remove -y mise")
            else:
                # Manual removal
                mise_bin = self._run_command("which mise")
                if mise_bin.returncode == 0:
                    mise_path = mise_bin.stdout.strip()
                    result = self._run_command(f"sudo rm -f {mise_path}")
                else:
                    logger.warning("Could not locate mise binary for removal")
                    result = None
            
            # Remove shell integration
            self._remove_mise_shell_integration()
            
            # Remove mise directory
            mise_dir = os.path.expanduser("~/.local/share/mise")
            if os.path.exists(mise_dir):
                self._run_command(f"rm -rf {mise_dir}")
            
            logger.info("mise uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall mise: {e}")
            return False
    
    def is_software_installed(self):
        """Check if mise is installed."""
        return self._command_exists("mise")
    
    def _setup_mise_shell_integration(self):
        """Set up mise shell integration."""
        logger.info("Setting up mise shell integration...")
        
        # Shell integration code
        bash_integration = '''
# mise
eval "$(mise activate bash)"
'''
        
        zsh_integration = '''
# mise
eval "$(mise activate zsh)"
'''
        
        # Add to shell profiles
        try:
            bash_profile = os.path.expanduser("~/.bashrc")
            if os.path.exists(bash_profile):
                with open(bash_profile, 'r') as f:
                    content = f.read()
                if 'mise activate' not in content:
                    with open(bash_profile, 'a') as f:
                        f.write(bash_integration)
                    logger.debug("Added mise integration to ~/.bashrc")
            
            zsh_profile = os.path.expanduser("~/.zshrc")
            if os.path.exists(zsh_profile):
                with open(zsh_profile, 'r') as f:
                    content = f.read()
                if 'mise activate' not in content:
                    with open(zsh_profile, 'a') as f:
                        f.write(zsh_integration)
                    logger.debug("Added mise integration to ~/.zshrc")
                    
        except Exception as e:
            logger.warning(f"Failed to set up shell integration: {e}")
    
    def _remove_mise_shell_integration(self):
        """Remove mise shell integration."""
        logger.info("Removing mise shell integration...")
        
        shell_files = ["~/.bashrc", "~/.zshrc", "~/.bash_profile"]
        
        for shell_file in shell_files:
            expanded_path = os.path.expanduser(shell_file)
            if os.path.exists(expanded_path):
                try:
                    # Remove mise-related lines
                    self._run_command(f"sed -i.bak '/mise activate/d' {expanded_path}")
                    self._run_command(f"sed -i.bak '/# mise/d' {expanded_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean {shell_file}: {e}")