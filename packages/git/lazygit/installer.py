import logging
from pathlib import Path
from ...base import BaseInstaller

logger = logging.getLogger(__name__)

class LazyGitInstaller(BaseInstaller):
    """Installer for lazygit - A simple terminal UI for git commands"""

    def __init__(self, package_name, category=None):
        super().__init__(package_name, category)
        self.binary_name = "lazygit"
    
    def install_software(self):
        """Install lazygit using system package manager or GitHub releases"""
        logger.info("Installing lazygit...")
        
        os_type = self._detect_os()
        
        # Try package manager first
        if self._install_via_package_manager():
            return True
        
        # Fallback to GitHub releases
        logger.info("Package manager installation failed or unavailable, trying GitHub releases...")
        return self._install_from_github()
    
    def _install_via_package_manager(self):
        """Install lazygit via system package manager"""
        package_manager, install_cmd = self._get_package_manager()
        
        if not package_manager:
            return False
        
        # Package names vary by distribution
        package_names = {
            "brew": "lazygit",
            "apt": "lazygit",
            "apt-get": "lazygit", 
            "dnf": "lazygit",
            "yum": "lazygit",
            "pacman": "lazygit",
            "winget": "JesseDuffield.lazygit",
            "choco": "lazygit"
        }
        
        package_name = package_names.get(package_manager)
        if not package_name:
            logger.debug(f"No package name mapping for {package_manager}")
            return False
        
        full_command = f"{install_cmd} {package_name}"
        logger.info(f"Installing lazygit using: {package_manager}")
        
        result = self._run_command(full_command)
        
        if result.returncode == 0:
            logger.info("lazygit installed successfully via package manager")
            return True
        else:
            logger.warning(f"Package manager installation failed: {result.stderr}")
            return False
    
    def _install_from_github(self):
        """Install lazygit from GitHub releases"""
        os_type = self._detect_os()
        
        # Detect architecture
        arch = self._detect_architecture()
        
        # Build download URL
        if os_type == "macos":
            if arch == "arm64":
                filename = "lazygit_*_Darwin_arm64.tar.gz"
            else:
                filename = "lazygit_*_Darwin_x86_64.tar.gz"
        elif os_type in ["linux", "debian", "redhat", "arch"]:
            if arch == "arm64":
                filename = "lazygit_*_Linux_arm64.tar.gz"
            else:
                filename = "lazygit_*_Linux_x86_64.tar.gz"
        elif os_type == "windows":
            filename = "lazygit_*_Windows_x86_64.zip"
        else:
            logger.error(f"Unsupported OS for GitHub installation: {os_type}")
            return False
        
        # Download and install
        install_script = f"""
        set -e
        TEMP_DIR=$(mktemp -d)
        cd "$TEMP_DIR"
        
        # Get latest release URL
        LATEST_URL=$(curl -s https://api.github.com/repos/jesseduffield/lazygit/releases/latest | grep browser_download_url | grep '{filename.replace('*', '[0-9.]+')}' | head -1 | cut -d '"' -f 4)
        
        if [ -z "$LATEST_URL" ]; then
            echo "Could not find download URL for {filename}"
            exit 1
        fi
        
        echo "Downloading: $LATEST_URL"
        curl -L -o lazygit.tar.gz "$LATEST_URL"
        
        # Extract
        tar xzf lazygit.tar.gz
        
        # Install to /usr/local/bin
        sudo mv lazygit /usr/local/bin/lazygit
        sudo chmod +x /usr/local/bin/lazygit
        
        # Cleanup
        cd /
        rm -rf "$TEMP_DIR"
        
        echo "lazygit installed successfully"
        """
        
        result = self._run_command(install_script)
        
        if result.returncode == 0:
            logger.info("lazygit installed successfully from GitHub")
            return True
        else:
            logger.error(f"GitHub installation failed: {result.stderr}")
            return False
          
    def uninstall_software(self):
        """Uninstall lazygit"""
        logger.info("Uninstalling lazygit...")
        
        # Try package manager first
        if self._uninstall_via_package_manager():
            return True
        
        # Fallback to manual removal
        logger.info("Package manager uninstall failed, trying manual removal...")
        return self._uninstall_manual()
    
    def _uninstall_via_package_manager(self):
        """Uninstall via package manager"""
        package_manager, _ = self._get_package_manager()
        
        if not package_manager:
            return False
        
        uninstall_commands = {
            "apt": "sudo apt remove -y lazygit",
            "apt-get": "sudo apt-get remove -y lazygit",
            "dnf": "sudo dnf remove -y lazygit",
            "yum": "sudo yum remove -y lazygit",
            "pacman": "sudo pacman -R --noconfirm lazygit",
            "brew": "brew uninstall lazygit",
            "winget": "winget uninstall JesseDuffield.lazygit",
            "choco": "choco uninstall -y lazygit"
        }
        
        uninstall_cmd = uninstall_commands.get(package_manager)
        if not uninstall_cmd:
            return False
        
        result = self._run_command(uninstall_cmd)
        
        if result.returncode == 0:
            logger.info("lazygit uninstalled successfully via package manager")
            return True
        else:
            logger.warning(f"Package manager uninstall failed: {result.stderr}")
            return False
    
    def _uninstall_manual(self):
        """Manually remove lazygit binary"""
        binary_path = self._find_lazygit_binary()
        
        if binary_path:
            try:
                # Try to remove with sudo if needed
                result = self._run_command(f"sudo rm -f {binary_path}")
                if result.returncode == 0:
                    logger.info("lazygit binary removed manually")
                    return True
                else:
                    logger.error("Failed to remove lazygit binary")
                    return False
            except Exception as e:
                logger.error(f"Manual removal failed: {e}")
                return False
        else:
            logger.warning("lazygit binary not found")
            return True
    
    def is_software_installed(self):
        """Check if lazygit is installed"""
        return self._command_exists(self.binary_name)
    
    def _find_lazygit_binary(self):
        """Find the lazygit binary location"""
        import shutil
        binary_location = shutil.which(self.binary_name)
        
        if binary_location:
            return Path(binary_location)
        return None
    
    def _detect_architecture(self):
        """Detect system architecture"""
        import platform
        
        arch = platform.machine().lower()
        if arch in ['arm64', 'aarch64']:
            return 'arm64'
        elif arch in ['x86_64', 'amd64']:
            return 'x86_64'
        else:
            return 'x86_64'  # Default fallback
    
    def setup_integration(self):
        """Setup lazygit integration - no additional setup needed"""
        logger.info("No additional integration setup needed for lazygit")
        return True
    
    def uninstall_integration(self):
        """Remove lazygit integration - no integration to remove"""
        logger.info("No integration to remove for lazygit")
        return True