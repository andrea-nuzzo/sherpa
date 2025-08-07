from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import shutil
import os

class BaseInstaller(ABC):
    """Abstract base class for all package installers."""
    
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
        pass

    def uninstall_config(self):
        """Remove configuration files (remove symlinks)"""
        pass

    def is_config_installed(self):
        """Check if configuration symlinks are already created."""
        pass
    
    def get_status(self):
        """Get installation status of both software and config."""
        pass
    
    # ==========================================
    # UTILITY METHODS - Helper functions
    # ==========================================
    
    def _ensure_stow_available(self):
        """Ensure stow is installed, install if missing"""
        pass
    
    def _is_config_installed(self):
        """Check if config is already stowed (simple check)."""
        pass
        
    def _run_command(self):
        """Run a shell command and return the result."""
        pass

    def _command_exists(self, command):
        """Check if a command exists in PATH."""
        return shutil.which(command) is not None
