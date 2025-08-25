import logging
import os
from packages.base import BaseInstaller

logger = logging.getLogger(__name__)

class NixInstaller(BaseInstaller):
    """Installer for Nix package manager."""
    
    def install_software(self):
        """Install Nix using the official installer."""
        logger.info("Installing Nix package manager...")
        
        if self.is_software_installed():
            logger.info("Nix is already installed")
            return True
        
        # Check OS support
        os_type = self._detect_os()
        if os_type not in ["linux", "macos"]:
            logger.error(f"Nix is not supported on {os_type}")
            return False
        
        try:
            # Use the official Nix installation script
            install_cmd = 'sh <(curl -L https://nixos.org/nix/install) --daemon'
            logger.info("Installing Nix with multi-user support (daemon mode)...")
            result = self._run_command(install_cmd)
            
            if result.returncode == 0:
                logger.info("Nix installed successfully")
                self._setup_nix_profile()
                return True
            else:
                # Try single-user installation as fallback
                logger.warning("Multi-user installation failed, trying single-user mode...")
                install_cmd = 'sh <(curl -L https://nixos.org/nix/install) --no-daemon'
                result = self._run_command(install_cmd)
                
                if result.returncode == 0:
                    logger.info("Nix installed successfully in single-user mode")
                    self._setup_nix_profile()
                    return True
                else:
                    logger.error(f"Nix installation failed: {result.stderr}")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to install Nix: {e}")
            return False
    
    def uninstall_software(self):
        """Uninstall Nix package manager."""
        logger.info("Uninstalling Nix...")
        
        if not self.is_software_installed():
            logger.info("Nix is not installed")
            return True
        
        try:
            # Check if it's a multi-user installation
            if os.path.exists("/nix/var/nix/daemon-socket"):
                logger.info("Detected multi-user Nix installation")
                # Stop the daemon
                self._run_command("sudo launchctl unload /Library/LaunchDaemons/org.nixos.nix-daemon.plist")
                # Remove the daemon plist
                self._run_command("sudo rm -f /Library/LaunchDaemons/org.nixos.nix-daemon.plist")
                # Remove users and groups
                for i in range(1, 33):  # nix build users 1-32
                    self._run_command(f"sudo dscl . -delete /Users/_nixbld{i}")
                    self._run_command(f"sudo dscl . -delete /Groups/nixbld")
            
            # Remove Nix store and configuration
            self._run_command("sudo rm -rf /nix")
            
            # Remove profile entries
            profile_files = [
                "~/.bash_profile",
                "~/.bashrc", 
                "~/.zshrc",
                "~/.profile"
            ]
            
            for profile_file in profile_files:
                expanded_path = os.path.expanduser(profile_file)
                if os.path.exists(expanded_path):
                    # Remove Nix-related lines
                    self._run_command(f"sed -i.bak '/nix/d' {expanded_path}")
            
            logger.info("Nix uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall Nix: {e}")
            return False
    
    def is_software_installed(self):
        """Check if Nix is installed."""
        return self._command_exists("nix") or self._command_exists("nix-env")
    
    def _setup_nix_profile(self):
        """Set up Nix profile for shell integration."""
        logger.info("Setting up Nix profile...")
        
        nix_profile_script = """
# Nix package manager
if [ -e ~/.nix-profile/etc/profile.d/nix.sh ]; then
    . ~/.nix-profile/etc/profile.d/nix.sh
fi
# End Nix
"""
        
        # Add to common shell profiles
        shell_profiles = [
            os.path.expanduser("~/.bashrc"),
            os.path.expanduser("~/.zshrc"),
            os.path.expanduser("~/.profile")
        ]
        
        for profile_path in shell_profiles:
            try:
                if os.path.exists(profile_path):
                    with open(profile_path, 'r') as f:
                        content = f.read()
                    
                    if 'nix-profile/etc/profile.d/nix.sh' not in content:
                        with open(profile_path, 'a') as f:
                            f.write(nix_profile_script)
                        logger.debug(f"Added Nix profile to {profile_path}")
            except Exception as e:
                logger.warning(f"Failed to update {profile_path}: {e}")
    
    def update_channels(self):
        """Update Nix channels."""
        logger.info("Updating Nix channels...")
        
        if not self.is_software_installed():
            logger.error("Nix is not available")
            return False
        
        try:
            result = self._run_command("nix-channel --update")
            
            if result.returncode == 0:
                logger.info("Nix channels updated successfully")
                return True
            else:
                logger.error(f"Failed to update Nix channels: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update Nix channels: {e}")
            return False