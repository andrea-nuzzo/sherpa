import logging
import os
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class HomeManagerInstaller(BaseInstaller):
    """Installer for Home Manager."""
    
    def install_software(self):
        """Install Home Manager using Nix."""
        logger.info("Installing Home Manager...")
        
        if self.is_software_installed():
            logger.info("Home Manager is already installed")
            return True
        
        # Check if Nix is available
        if not self._command_exists("nix"):
            logger.error("Nix is required but not found. Please install Nix first.")
            return False
        
        try:
            # Add the Home Manager channel
            logger.info("Adding Home Manager channel...")
            channel_cmd = "nix-channel --add https://github.com/nix-community/home-manager/archive/master.tar.gz home-manager"
            result = self._run_command(channel_cmd)
            
            if result.returncode != 0:
                logger.error(f"Failed to add Home Manager channel: {result.stderr}")
                return False
            
            # Update channels
            logger.info("Updating Nix channels...")
            update_cmd = "nix-channel --update"
            result = self._run_command(update_cmd)
            
            if result.returncode != 0:
                logger.error(f"Failed to update channels: {result.stderr}")
                return False
            
            # Install Home Manager
            logger.info("Installing Home Manager...")
            install_cmd = "nix-shell '<home-manager>' -A install"
            result = self._run_command(install_cmd)
            
            if result.returncode == 0:
                logger.info("Home Manager installed successfully")
                self._setup_home_manager()
                return True
            else:
                logger.error(f"Home Manager installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install Home Manager: {e}")
            return False
    
    def uninstall_software(self):
        """Uninstall Home Manager."""
        logger.info("Uninstalling Home Manager...")
        
        if not self.is_software_installed():
            logger.info("Home Manager is not installed")
            return True
        
        try:
            # Remove Home Manager
            logger.info("Removing Home Manager...")
            uninstall_cmd = "home-manager uninstall"
            result = self._run_command(uninstall_cmd)
            
            # Remove the channel
            logger.info("Removing Home Manager channel...")
            remove_channel_cmd = "nix-channel --remove home-manager"
            self._run_command(remove_channel_cmd)
            
            # Remove configuration files
            config_dir = os.path.expanduser("~/.config/nixpkgs")
            if os.path.exists(config_dir):
                self._run_command(f"rm -rf {config_dir}")
            
            logger.info("Home Manager uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall Home Manager: {e}")
            return False
    
    def is_software_installed(self):
        """Check if Home Manager is installed."""
        return self._command_exists("home-manager")
    
    def _setup_home_manager(self):
        """Set up basic Home Manager configuration."""
        logger.info("Setting up Home Manager configuration...")
        
        config_dir = os.path.expanduser("~/.config/nixpkgs")
        config_file = os.path.join(config_dir, "home.nix")
        
        try:
            # Create config directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
            
            # Create basic home.nix if it doesn't exist
            if not os.path.exists(config_file):
                basic_config = '''{ config, pkgs, ... }:

{
  # Home Manager needs a bit of information about you and the
  # paths it should manage.
  home.username = "''' + os.getenv("USER", "user") + '''";
  home.homeDirectory = "''' + os.path.expanduser("~") + '''";

  # This value determines the Home Manager release that your
  # configuration is compatible with. This helps avoid breakage
  # when a new Home Manager release introduces backwards
  # incompatible changes.
  #
  # You can update Home Manager without changing this value. See
  # the Home Manager release notes for a list of state version
  # changes in each release.
  home.stateVersion = "23.11";

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;
}
'''
                
                with open(config_file, 'w') as f:
                    f.write(basic_config)
                
                logger.info(f"Created basic Home Manager configuration at {config_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set up Home Manager configuration: {e}")
            return False
    
    def switch_configuration(self):
        """Apply Home Manager configuration."""
        logger.info("Applying Home Manager configuration...")
        
        if not self.is_software_installed():
            logger.error("Home Manager is not available")
            return False
        
        try:
            result = self._run_command("home-manager switch")
            
            if result.returncode == 0:
                logger.info("Home Manager configuration applied successfully")
                return True
            else:
                logger.error(f"Failed to apply Home Manager configuration: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply Home Manager configuration: {e}")
            return False