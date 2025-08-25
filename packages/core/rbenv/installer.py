import logging
import os
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class RbenvInstaller(BaseInstaller):
    """Installer for rbenv Ruby version manager."""
    
    def install_software(self):
        """Install rbenv using git clone or package manager."""
        logger.info("Installing rbenv...")
        
        if self.is_software_installed():
            logger.info("rbenv is already installed")
            return True
        
        # Try package manager first
        if self._install_via_package_manager():
            return True
        
        # Fallback to git installation
        try:
            # Clone rbenv repository
            rbenv_dir = os.path.expanduser("~/.rbenv")
            clone_cmd = f"git clone https://github.com/rbenv/rbenv.git {rbenv_dir}"
            result = self._run_command(clone_cmd)
            
            if result.returncode == 0:
                # Also install ruby-build plugin
                plugins_dir = os.path.join(rbenv_dir, "plugins")
                os.makedirs(plugins_dir, exist_ok=True)
                ruby_build_cmd = f"git clone https://github.com/rbenv/ruby-build.git {plugins_dir}/ruby-build"
                self._run_command(ruby_build_cmd)
                
                logger.info("rbenv installed successfully")
                self._setup_rbenv_shell_integration()
                return True
            else:
                logger.error(f"rbenv installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install rbenv: {e}")
            return False
    
    def _install_via_package_manager(self):
        """Install rbenv via system package manager."""
        logger.info("Trying to install rbenv via package manager...")
        
        package_manager, install_cmd = self._get_package_manager()
        if not package_manager:
            return False
        
        try:
            if package_manager == "brew":
                result = self._run_command("brew install rbenv ruby-build")
            elif package_manager == "apt":
                # Install dependencies first
                self._run_command("sudo apt update")
                self._run_command("sudo apt install -y git curl libssl-dev libreadline-dev zlib1g-dev autoconf bison build-essential libyaml-dev libreadline-dev libncurses5-dev libffi-dev libgdbm-dev")
                # rbenv is not in standard apt repos, so we'll return false
                return False
            else:
                return False
            
            if result and result.returncode == 0:
                logger.info("rbenv installed successfully via package manager")
                self._setup_rbenv_shell_integration()
                return True
            else:
                return False
                
        except Exception as e:
            logger.debug(f"Package manager installation failed: {e}")
            return False
    
    def uninstall_software(self):
        """Uninstall rbenv."""
        logger.info("Uninstalling rbenv...")
        
        if not self.is_software_installed():
            logger.info("rbenv is not installed")
            return True
        
        try:
            package_manager, _ = self._get_package_manager()
            
            if package_manager == "brew" and self._command_exists("brew"):
                result = self._run_command("brew uninstall rbenv ruby-build")
            else:
                # Remove rbenv directory (typical git installation)
                rbenv_dir = os.path.expanduser("~/.rbenv")
                if os.path.exists(rbenv_dir):
                    result = self._run_command(f"rm -rf {rbenv_dir}")
                else:
                    logger.warning("Could not locate rbenv installation directory")
                    result = None
            
            # Remove shell integration
            self._remove_rbenv_shell_integration()
            
            logger.info("rbenv uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall rbenv: {e}")
            return False
    
    def is_software_installed(self):
        """Check if rbenv is installed."""
        return self._command_exists("rbenv") or os.path.exists(os.path.expanduser("~/.rbenv/bin/rbenv"))
    
    def _setup_rbenv_shell_integration(self):
        """Set up rbenv shell integration."""
        logger.info("Setting up rbenv shell integration...")
        
        # Shell integration code for different installation methods
        git_integration = '''
# rbenv
export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"
'''
        
        brew_integration = '''
# rbenv
eval "$(rbenv init - bash)"
'''
        
        # Determine which integration to use
        if os.path.exists(os.path.expanduser("~/.rbenv/bin/rbenv")):
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
                    if 'rbenv init' not in content:
                        with open(expanded_path, 'a') as f:
                            f.write(integration)
                        logger.debug(f"Added rbenv integration to {shell_file}")
                        
        except Exception as e:
            logger.warning(f"Failed to set up shell integration: {e}")
    
    def _remove_rbenv_shell_integration(self):
        """Remove rbenv shell integration."""
        logger.info("Removing rbenv shell integration...")
        
        shell_files = ["~/.bashrc", "~/.zshrc", "~/.bash_profile"]
        
        for shell_file in shell_files:
            expanded_path = os.path.expanduser(shell_file)
            if os.path.exists(expanded_path):
                try:
                    # Remove rbenv-related lines
                    self._run_command(f"sed -i.bak '/rbenv init/d' {expanded_path}")
                    self._run_command(f"sed -i.bak '/\\.rbenv\\/bin/d' {expanded_path}")
                    self._run_command(f"sed -i.bak '/# rbenv/d' {expanded_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean {shell_file}: {e}")