import logging
from pathlib import Path
from ...base import BaseInstaller

logger = logging.getLogger(__name__)

class GhosttyInstaller(BaseInstaller):
    """Installer for Ghostty - A fast, feature-rich, and cross-platform terminal emulator"""

    def __init__(self, package_name, category=None):
        super().__init__(package_name, category)
        self.binary_name = "ghostty"
    
    def install_software(self):
        """Install Ghostty - only supported on macOS and Linux"""
        logger.info("Installing Ghostty...")
        
        os_type = self._detect_os()
        
        # Check if OS is supported
        if os_type == "windows":
            logger.error("Ghostty is not available for Windows")
            return False
        
        # Try package manager first
        if self._install_via_package_manager():
            return True
        
        # Fallback to GitHub releases for Linux
        if os_type in ["linux", "debian", "redhat", "arch"]:
            logger.info("Package manager installation failed, trying GitHub releases...")
            return self._install_from_github()
        
        logger.error(f"No installation method available for {os_type}")
        return False
    
    def _install_via_package_manager(self):
        """Install Ghostty via system package manager"""
        package_manager, install_cmd = self._get_package_manager()
        
        if not package_manager:
            return False
        
        # Package names vary by distribution
        package_names = {
            "brew": "ghostty",
            "apt": "ghostty",
            "apt-get": "ghostty", 
            "dnf": "ghostty",
            "yum": "ghostty",
            "pacman": "ghostty-git"  # AUR package
        }
        
        package_name = package_names.get(package_manager)
        if not package_name:
            logger.debug(f"No package name mapping for {package_manager}")
            return False
        
        # Special handling for AUR packages
        if package_manager == "pacman" and package_name == "ghostty-git":
            logger.info("Installing from AUR requires yay or paru")
            # Try with yay first, then paru
            for aur_helper in ["yay", "paru"]:
                if self._command_exists(aur_helper):
                    full_command = f"{aur_helper} -S --noconfirm {package_name}"
                    logger.info(f"Installing Ghostty using AUR helper: {aur_helper}")
                    result = self._run_command(full_command)
                    if result.returncode == 0:
                        logger.info("Ghostty installed successfully via AUR")
                        return True
            logger.warning("No AUR helper (yay/paru) found for Arch Linux installation")
            return False
        
        full_command = f"{install_cmd} {package_name}"
        logger.info(f"Installing Ghostty using: {package_manager}")
        
        result = self._run_command(full_command)
        
        if result.returncode == 0:
            logger.info("Ghostty installed successfully via package manager")
            return True
        else:
            logger.warning(f"Package manager installation failed: {result.stderr}")
            return False
    
    def _install_from_github(self):
        """Install Ghostty from GitHub releases (Linux only)"""
        os_type = self._detect_os()
        
        if os_type == "macos":
            logger.error("GitHub installation not supported on macOS, use Homebrew")
            return False
        
        # Detect architecture
        arch = self._detect_architecture()
        
        # Build download URL pattern for Linux
        if arch == "arm64":
            filename = "ghostty-linux-aarch64.tar.xz"
        else:
            filename = "ghostty-linux-x86_64.tar.xz"
        
        # Download and install
        install_script = f"""
        set -e
        TEMP_DIR=$(mktemp -d)
        cd "$TEMP_DIR"
        
        # Get latest release URL
        LATEST_URL=$(curl -s https://api.github.com/repos/ghostty-org/ghostty/releases/latest | grep browser_download_url | grep '{filename}' | head -1 | cut -d '"' -f 4)
        
        if [ -z "$LATEST_URL" ]; then
            echo "Could not find download URL for {filename}"
            exit 1
        fi
        
        echo "Downloading: $LATEST_URL"
        curl -L -o ghostty.tar.xz "$LATEST_URL"
        
        # Extract
        tar xf ghostty.tar.xz
        
        # Install binary
        sudo install -Dm755 ghostty-*/ghostty /usr/local/bin/ghostty
        
        # Install desktop file (if exists)
        if [ -f ghostty-*/ghostty.desktop ]; then
            sudo install -Dm644 ghostty-*/ghostty.desktop /usr/share/applications/ghostty.desktop
        fi
        
        # Install icon (if exists)
        if [ -f ghostty-*/ghostty.png ]; then
            sudo install -Dm644 ghostty-*/ghostty.png /usr/share/pixmaps/ghostty.png
        fi
        
        # Cleanup
        cd /
        rm -rf "$TEMP_DIR"
        
        echo "Ghostty installed successfully"
        """
        
        result = self._run_command(install_script)
        
        if result.returncode == 0:
            logger.info("Ghostty installed successfully from GitHub")
            return True
        else:
            logger.error(f"GitHub installation failed: {result.stderr}")
            return False
          
    def uninstall_software(self):
        """Uninstall Ghostty"""
        logger.info("Uninstalling Ghostty...")
        
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
            "apt": "sudo apt remove -y ghostty",
            "apt-get": "sudo apt-get remove -y ghostty",
            "dnf": "sudo dnf remove -y ghostty",
            "yum": "sudo yum remove -y ghostty",
            "pacman": "sudo pacman -R --noconfirm ghostty-git",
            "brew": "brew uninstall ghostty"
        }
        
        uninstall_cmd = uninstall_commands.get(package_manager)
        if not uninstall_cmd:
            # Try AUR helpers for Arch
            if package_manager == "pacman":
                for aur_helper in ["yay", "paru"]:
                    if self._command_exists(aur_helper):
                        result = self._run_command(f"{aur_helper} -R --noconfirm ghostty-git")
                        if result.returncode == 0:
                            logger.info("Ghostty uninstalled successfully via AUR")
                            return True
            return False
        
        result = self._run_command(uninstall_cmd)
        
        if result.returncode == 0:
            logger.info("Ghostty uninstalled successfully via package manager")
            return True
        else:
            logger.warning(f"Package manager uninstall failed: {result.stderr}")
            return False
    
    def _uninstall_manual(self):
        """Manually remove Ghostty"""
        logger.info("Performing manual Ghostty removal...")
        
        cleanup_script = """
        set -e
        
        # Remove binary
        sudo rm -f /usr/local/bin/ghostty
        sudo rm -f /usr/bin/ghostty
        
        # Remove desktop file
        sudo rm -f /usr/share/applications/ghostty.desktop
        
        # Remove icon
        sudo rm -f /usr/share/pixmaps/ghostty.png
        
        # Remove any remaining files in common locations
        sudo rm -rf /usr/local/share/ghostty
        sudo rm -rf /usr/share/ghostty
        
        echo "Ghostty removed manually"
        """
        
        result = self._run_command(cleanup_script)
        
        if result.returncode == 0:
            logger.info("Ghostty removed manually")
            return True
        else:
            logger.error(f"Manual removal failed: {result.stderr}")
            return False
    
    def is_software_installed(self):
        """Check if Ghostty is installed"""
        return self._command_exists(self.binary_name)
    
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
        """Setup Ghostty integration"""
        logger.info("Setting up Ghostty integration...")
        
        os_type = self._detect_os()
        
        if os_type == "macos":
            # On macOS, Ghostty should be available in Applications
            logger.info("Ghostty should be available in your Applications folder")
        else:
            # On Linux, check if desktop file is available
            desktop_file = Path("/usr/share/applications/ghostty.desktop")
            if desktop_file.exists():
                logger.info("Ghostty desktop entry installed, available in application menu")
            else:
                logger.info("Ghostty available via command line: ghostty")
        
        # Verify installation
        if self.is_software_installed():
            result = self._run_command("ghostty --version")
            if result.returncode == 0:
                logger.info(f"Ghostty integration complete: {result.stdout.strip()}")
                return True
        
        logger.warning("Ghostty integration may not be complete")
        return False
    
    def uninstall_integration(self):
        """Remove Ghostty integration"""
        logger.info("Removing Ghostty integration...")
        logger.info("No additional integration cleanup needed")
        return True