import os
import subprocess
import platform
import sys
import shutil
import logging
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseInstaller(ABC):
    """Abstract base class for all package installers."""
    
    def __init__(self, package_name):
        self.package_name = package_name
        self.package_dir = Path("packages") / package_name
        self.config_dir = self.package_dir / "config"

        logger.debug(f"Initializing installer for {package_name}")
        
        # Validate package structure
        if not self.package_dir.exists():
            raise FileNotFoundError(f"Package directory not found: {self.package_dir}")
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")
            
        logger.info(f"Package {package_name} structure validated")
    
    # ==========================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # ==========================================
    
    @abstractmethod
    def install_software(self):
        """
        Install the actual software (binary/package).
        Each package has different installation method.
        
        Examples:
        - Starship: curl install script
        - Git: apt install git / brew install git
        - Zsh: apt install zsh / brew install zsh
        """
        pass
    
    @abstractmethod
    def uninstall_software(self):
        """
        Remove the software from system.
        Each package has different removal method.
        """
        pass
    
    @abstractmethod
    def is_software_installed(self):
        """
        Check if the software is already installed.
        Return True if installed, False otherwise.
        
        Examples:
        - Check if binary exists in PATH
        - Check if package is installed via package manager
        """
        pass
    
    # ==========================================
    # CONCRETE METHODS - Shared implementation
    # ==========================================
    
    def install_config(self):
        """Install configuration files using stow-like functionality"""
        logger.info(f"Installing configuration for {self.package_name}")
        
        if not self._ensure_stow_available():
            logger.error("Stow is not available, cannot install config")
            return
        
        try:
            # Use stow to symlink config files
            cmd = f"stow -d {self.package_dir.parent} -t {self.home_dir} {self.package_name}"
            result = self._run_command(cmd)
            
            if result.returncode == 0:
                logger.info(f"Config installed successfully for {self.package_name}")
                return True
            else:
                logger.error(f"Config installation failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Config installation failed: {e}")
            return False

    def uninstall_config(self):
        """Remove configuration files (remove symlinks)"""
        pass

    def is_config_installed(self):
        """Check if configuration symlinks are already created."""
        return self._is_config_installed()
    
    def get_status(self):
        """Get installation status of both software and config."""
        return {
            "package": self.package_name,
            "software_installed": self.is_software_installed(),
            "config_installed": self.is_config_installed()
        }

    # ==========================================
    # UTILITY METHODS - Helper functions
    # ==========================================
    
    def _detect_os(self):
        """Detect the operating system."""
        system = platform.system().lower()
        
        if system == "linux":
            # Check for specific Linux distributions
            try:
                with open("/etc/os-release", "r") as f:
                    os_release = f.read().lower()
                    if "ubuntu" in os_release or "debian" in os_release:
                        return "debian"
                    elif "centos" in os_release or "rhel" in os_release or "fedora" in os_release:
                        return "redhat"
                    elif "arch" in os_release:
                        return "arch"
                    else:
                        return "linux"
            except FileNotFoundError:
                return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"
    
    def _get_package_manager(self):    
        """Get the appropriate package manager for the current OS"""
        os_type = self._detect_os()
        
        package_managers = {
            "debian": [
                ("apt", "sudo apt update && sudo apt install -y"),
                ("apt-get", "sudo apt-get update && sudo apt-get install -y")
            ],
            "redhat": [
                ("dnf", "sudo dnf install -y"),
                ("yum", "sudo yum install -y")
            ],
            "arch": [
                ("pacman", "sudo pacman -S --noconfirm")
            ],
            "macos": [
                ("brew", "brew install")
            ],
            "windows": [
                ("winget", "winget install"),
                ("choco", "choco install -y")
            ]
        }
        
        # Get package managers for detected OS
        managers = package_managers.get(os_type, [])
        
        # Return the first available package manager
        for manager, install_cmd in managers:
            if self._command_exists(manager):
                logger.debug(f"Using package manager: {manager}")
                return manager, install_cmd
        
        logger.warning(f"No supported package manager found for OS: {os_type}")
        return None, None
    
    def _ensure_stow_available(self):
        """Ensure stow is installed, install if missing"""
        if self._command_exists("stow"):
            logger.debug("Stow is already available")
            return True
        
        logger.info("📦 Stow not found, attempting to install...")
        
        try:
            package_manager, install_cmd = self._get_package_manager()
            
            if not package_manager:
                logger.error("Cannot install stow: no supported package manager found")
                return False
            
            # Install stow
            full_command = f"{install_cmd} stow"
            logger.info(f"Installing stow using: {package_manager}")
            self._run_command(full_command)
            
            # Verify installation
            if self._command_exists("stow"):
                logger.info("Stow installed successfully")
                return True
            else:
                logger.error("Stow installation failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install stow: {e}")
            logger.info("Please install stow manually and try again")
            return False
    
    def _is_config_installed(self):
        """Check if config is already stowed (simple check)."""
        for config_file in self.config_dir.rglob("*"):
            if config_file.is_file():
                # Calculate the relative path from config_dir
                rel_path = config_file.relative_to(self.config_dir)
                target_path = self.home_dir / rel_path

                # If the target exists and is a symlink pointing to our file
                if target_path.exists() and target_path.is_symlink():
                    if target_path.resolve() == config_file.resolve():
                        return True
        return False

    def _run_command(self, command, shell=True, capture_output=True, text=True):
        """Run a shell command and return the result."""
        logger.debug(f"Running command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=capture_output,
                text=text,
                check=False # Don't raise exception on non-zero exit
            )
            if result.stdout:
                logger.debug(f"Command output: {result.stdout.strip()}")
            if result.stderr:
                logger.debug(f"Command error: {result.stderr.strip()}")
                
            return result
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise

    def _command_exists(self, command):
        """Check if a command exists in PATH."""
        return shutil.which(command) is not None
