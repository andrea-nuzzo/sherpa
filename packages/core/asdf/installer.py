import logging
import os
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class AsdfInstaller(BaseInstaller):
    """Installer for asdf version manager."""
    
    def install_software(self):
        """Install asdf using git clone method."""
        logger.info("Installing asdf...")
        
        if self.is_software_installed():
            logger.info("asdf is already installed")
            return True
        
        try:
            # Clone asdf repository
            asdf_dir = os.path.expanduser("~/.asdf")
            clone_cmd = f"git clone https://github.com/asdf-vm/asdf.git {asdf_dir} --branch v0.13.1"
            result = self._run_command(clone_cmd)
            
            if result.returncode == 0:
                logger.info("asdf installed successfully")
                self._setup_asdf_shell_integration()
                return True
            else:
                logger.error(f"asdf installation failed: {result.stderr}")
                return self._install_via_package_manager()
                
        except Exception as e:
            logger.error(f"Failed to install asdf: {e}")
            return self._install_via_package_manager()
    
    def _install_via_package_manager(self):
        """Install asdf via system package manager as fallback."""
        logger.info("Trying to install asdf via package manager...")
        
        package_manager, install_cmd = self._get_package_manager()
        if not package_manager:
            logger.error("No package manager available")
            return False
        
        try:
            if package_manager == "brew":
                result = self._run_command("brew install asdf")
            else:
                logger.warning(f"Package manager {package_manager} not fully supported for asdf")
                return False
            
            if result.returncode == 0:
                logger.info("asdf installed successfully via package manager")
                self._setup_asdf_shell_integration()
                return True
            else:
                logger.error(f"Failed to install asdf via package manager: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install asdf via package manager: {e}")
            return False
    
    def uninstall_software(self):
        """Uninstall asdf."""
        logger.info("Uninstalling asdf...")
        
        if not self.is_software_installed():
            logger.info("asdf is not installed")
            return True
        
        try:
            package_manager, _ = self._get_package_manager()
            
            if package_manager == "brew" and self._command_exists("brew"):
                result = self._run_command("brew uninstall asdf")
            else:
                # Remove asdf directory (typical installation)
                asdf_dir = os.path.expanduser("~/.asdf")
                if os.path.exists(asdf_dir):
                    result = self._run_command(f"rm -rf {asdf_dir}")
                else:
                    logger.warning("Could not locate asdf installation directory")
                    result = None
            
            # Remove shell integration
            self._remove_asdf_shell_integration()
            
            logger.info("asdf uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall asdf: {e}")
            return False
    
    def is_software_installed(self):
        """Check if asdf is installed."""
        return self._command_exists("asdf") or os.path.exists(os.path.expanduser("~/.asdf/bin/asdf"))
    
    def _setup_asdf_shell_integration(self):
        """Set up asdf shell integration."""
        logger.info("Setting up asdf shell integration...")
        
        # Shell integration code for different installation methods
        git_integration = '''
# asdf
. "$HOME/.asdf/asdf.sh"
. "$HOME/.asdf/completions/asdf.bash"
'''
        
        brew_integration = '''
# asdf
. $(brew --prefix asdf)/libexec/asdf.sh
'''
        
        # Determine which integration to use
        if os.path.exists(os.path.expanduser("~/.asdf/asdf.sh")):
            integration = git_integration
        elif self._command_exists("brew"):
            integration = brew_integration
        else:
            integration = git_integration  # fallback
        
        # Add to shell profiles
        try:
            for shell_file in ["~/.bashrc", "~/.zshrc", "~/.bash_profile"]:
                expanded_path = os.path.expanduser(shell_file)
                if os.path.exists(expanded_path):
                    with open(expanded_path, 'r') as f:
                        content = f.read()
                    if 'asdf.sh' not in content:
                        with open(expanded_path, 'a') as f:
                            f.write(integration)
                        logger.debug(f"Added asdf integration to {shell_file}")
                        
        except Exception as e:
            logger.warning(f"Failed to set up shell integration: {e}")
    
    def _remove_asdf_shell_integration(self):
        """Remove asdf shell integration."""
        logger.info("Removing asdf shell integration...")
        
        shell_files = ["~/.bashrc", "~/.zshrc", "~/.bash_profile"]
        
        for shell_file in shell_files:
            expanded_path = os.path.expanduser(shell_file)
            if os.path.exists(expanded_path):
                try:
                    # Remove asdf-related lines
                    self._run_command(f"sed -i.bak '/asdf.sh/d' {expanded_path}")
                    self._run_command(f"sed -i.bak '/asdf.bash/d' {expanded_path}")
                    self._run_command(f"sed -i.bak '/# asdf/d' {expanded_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean {shell_file}: {e}")