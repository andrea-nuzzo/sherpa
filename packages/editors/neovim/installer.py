import logging
from pathlib import Path
from ...base import BaseInstaller

logger = logging.getLogger(__name__)

class NeovimInstaller(BaseInstaller):
    """Installer for Neovim with LazyVim configuration"""

    def __init__(self, package_name, category=None):
        super().__init__(package_name, category)
        self.binary_name = "nvim"
    
    def install_software(self):
        """Install Neovim using system package manager or GitHub releases"""
        logger.info("Installing Neovim...")
        
        # Try package manager first
        if self._install_via_package_manager():
            return True
        
        # Fallback to GitHub releases
        logger.info("Package manager installation failed or unavailable, trying GitHub releases...")
        return self._install_from_github()
    
    def _install_via_package_manager(self):
        """Install Neovim via system package manager"""
        package_manager, install_cmd = self._get_package_manager()
        
        if not package_manager:
            return False
        
        # Package names vary by distribution
        package_names = {
            "brew": "neovim",
            "apt": "neovim",
            "apt-get": "neovim", 
            "dnf": "neovim",
            "yum": "neovim",
            "pacman": "neovim",
            "winget": "Neovim.Neovim",
            "choco": "neovim"
        }
        
        package_name = package_names.get(package_manager)
        if not package_name:
            logger.debug(f"No package name mapping for {package_manager}")
            return False
        
        full_command = f"{install_cmd} {package_name}"
        logger.info(f"Installing Neovim using: {package_manager}")
        
        result = self._run_command(full_command)
        
        if result.returncode == 0:
            logger.info("Neovim installed successfully via package manager")
            return True
        else:
            logger.warning(f"Package manager installation failed: {result.stderr}")
            return False
    
    def _install_from_github(self):
        """Install Neovim from GitHub releases"""
        os_type = self._detect_os()
        
        # Detect architecture
        arch = self._detect_architecture()
        
        # Build download URL pattern
        if os_type == "macos":
            filename = "nvim-macos-*.tar.gz"
        elif os_type in ["linux", "debian", "redhat", "arch"]:
            filename = "nvim-linux64.tar.gz"
        elif os_type == "windows":
            filename = "nvim-win64.zip"
        else:
            logger.error(f"Unsupported OS for GitHub installation: {os_type}")
            return False
        
        # Download and install
        if os_type == "windows":
            install_script = f"""
            $tempDir = New-TemporaryFile | %{{Remove-Item $_; New-Item -ItemType Directory -Path $_}}
            cd $tempDir
            
            # Get latest release URL
            $latestUrl = (Invoke-RestMethod -Uri "https://api.github.com/repos/neovim/neovim/releases/latest").assets | Where-Object {{$_.name -like "{filename.replace('*', '*')}"}} | Select-Object -First 1 | %{{$_.browser_download_url}}
            
            if (-not $latestUrl) {{
                Write-Error "Could not find download URL for {filename}"
                exit 1
            }}
            
            Write-Host "Downloading: $latestUrl"
            Invoke-WebRequest -Uri $latestUrl -OutFile "neovim.zip"
            
            # Extract
            Expand-Archive -Path "neovim.zip" -DestinationPath "."
            
            # Install to Program Files
            $installPath = "$env:ProgramFiles\\Neovim"
            if (Test-Path $installPath) {{
                Remove-Item -Path $installPath -Recurse -Force
            }}
            Move-Item -Path "nvim-win64" -Destination $installPath
            
            # Add to PATH
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
            $binPath = "$installPath\\bin"
            if ($currentPath -notlike "*$binPath*") {{
                [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binPath", "Machine")
            }}
            
            Write-Host "Neovim installed successfully"
            """
        else:
            install_script = f"""
            set -e
            TEMP_DIR=$(mktemp -d)
            cd "$TEMP_DIR"
            
            # Get latest release URL
            LATEST_URL=$(curl -s https://api.github.com/repos/neovim/neovim/releases/latest | grep browser_download_url | grep '{filename.replace('*', '[0-9.]+')}' | head -1 | cut -d '"' -f 4)
            
            if [ -z "$LATEST_URL" ]; then
                echo "Could not find download URL for {filename}"
                exit 1
            fi
            
            echo "Downloading: $LATEST_URL"
            curl -L -o neovim.tar.gz "$LATEST_URL"
            
            # Extract
            tar xzf neovim.tar.gz
            
            # Install to /usr/local
            sudo rm -rf /usr/local/nvim-*
            sudo mv nvim-* /usr/local/nvim
            
            # Create symlink
            sudo ln -sf /usr/local/nvim/bin/nvim /usr/local/bin/nvim
            
            # Cleanup
            cd /
            rm -rf "$TEMP_DIR"
            
            echo "Neovim installed successfully"
            """
        
        result = self._run_command(install_script)
        
        if result.returncode == 0:
            logger.info("Neovim installed successfully from GitHub")
            return True
        else:
            logger.error(f"GitHub installation failed: {result.stderr}")
            return False
          
    def uninstall_software(self):
        """Uninstall Neovim"""
        logger.info("Uninstalling Neovim...")
        
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
            "apt": "sudo apt remove -y neovim",
            "apt-get": "sudo apt-get remove -y neovim",
            "dnf": "sudo dnf remove -y neovim",
            "yum": "sudo yum remove -y neovim",
            "pacman": "sudo pacman -R --noconfirm neovim",
            "brew": "brew uninstall neovim",
            "winget": "winget uninstall Neovim.Neovim",
            "choco": "choco uninstall -y neovim"
        }
        
        uninstall_cmd = uninstall_commands.get(package_manager)
        if not uninstall_cmd:
            return False
        
        result = self._run_command(uninstall_cmd)
        
        if result.returncode == 0:
            logger.info("Neovim uninstalled successfully via package manager")
            return True
        else:
            logger.warning(f"Package manager uninstall failed: {result.stderr}")
            return False
    
    def _uninstall_manual(self):
        """Manually remove Neovim"""
        os_type = self._detect_os()
        
        if os_type == "windows":
            cleanup_script = """
            # Remove from Program Files
            $installPath = "$env:ProgramFiles\\Neovim"
            if (Test-Path $installPath) {
                Remove-Item -Path $installPath -Recurse -Force
            }
            
            # Remove from PATH
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
            $binPath = "$installPath\\bin"
            $newPath = ($currentPath -split ";") | Where-Object { $_ -ne $binPath } | Join-String -Separator ";"
            [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
            
            Write-Host "Neovim removed manually"
            """
        else:
            cleanup_script = """
            set -e
            
            # Remove symlink
            sudo rm -f /usr/local/bin/nvim
            
            # Remove installation directory
            sudo rm -rf /usr/local/nvim*
            
            echo "Neovim removed manually"
            """
        
        result = self._run_command(cleanup_script)
        
        if result.returncode == 0:
            logger.info("Neovim removed manually")
            return True
        else:
            logger.error(f"Manual removal failed: {result.stderr}")
            return False
    
    def is_software_installed(self):
        """Check if Neovim is installed"""
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
        """Setup Neovim with LazyVim integration"""
        logger.info("Setting up Neovim with LazyVim integration...")
        
        # Verify Neovim installation
        if not self.is_software_installed():
            logger.error("Neovim not found, cannot setup LazyVim")
            return False
        
        # Check Neovim version (LazyVim requires 0.8+)
        result = self._run_command("nvim --version")
        if result.returncode != 0:
            logger.error("Could not determine Neovim version")
            return False
        
        version_output = result.stdout.split('\n')[0]
        logger.info(f"Found Neovim: {version_output}")
        
        # Check if we have a recent enough version
        try:
            version_line = version_output.lower()
            if "v0." in version_line:
                # Extract version number
                import re
                match = re.search(r'v0\.(\d+)', version_line)
                if match:
                    minor_version = int(match.group(1))
                    if minor_version < 8:
                        logger.warning(f"LazyVim requires Neovim 0.8+, found 0.{minor_version}")
                        logger.info("Continuing anyway, but LazyVim may not work properly")
        except Exception as e:
            logger.debug(f"Could not parse version: {e}")
        
        # Setup LazyVim by cloning the starter configuration
        return self._setup_lazyvim()
    
    def _setup_lazyvim(self):
        """Setup custom LazyVim configuration"""
        logger.info("Setting up custom LazyVim configuration...")
        
        os_type = self._detect_os()
        
        # Determine Neovim config directory
        if os_type == "windows":
            nvim_config_dir = Path.home() / "AppData" / "Local" / "nvim"
        else:
            nvim_config_dir = Path.home() / ".config" / "nvim"
        
        # Backup existing config if it exists
        if nvim_config_dir.exists():
            backup_dir = nvim_config_dir.parent / f"nvim.bak.{self._get_timestamp()}"
            logger.info(f"Backing up existing Neovim config to: {backup_dir}")
            
            if os_type == "windows":
                backup_script = f'Move-Item -Path "{nvim_config_dir}" -Destination "{backup_dir}"'
            else:
                backup_script = f'mv "{nvim_config_dir}" "{backup_dir}"'
            
            result = self._run_command(backup_script)
            if result.returncode != 0:
                logger.warning("Failed to backup existing config")
        
        # The configuration will be installed via stow from the sherpa config
        # This happens automatically when the config is installed
        logger.info("Custom LazyVim configuration will be symlinked via stow")
        
        # Create additional symlink to standard XDG config location if needed
        standard_config_dir = Path.home() / ".config" / "nvim"
        stow_config_dir = Path.home() / "config" / "nvim"
        
        if not standard_config_dir.exists() and stow_config_dir.exists():
            logger.info("Creating symlink from standard XDG config location to stow location")
            try:
                # Ensure .config directory exists
                standard_config_dir.parent.mkdir(exist_ok=True)
                # Create symlink
                if os_type == "windows":
                    import subprocess
                    subprocess.run(["mklink", "/D", str(standard_config_dir), str(stow_config_dir)], shell=True)
                else:
                    standard_config_dir.symlink_to(stow_config_dir)
                logger.info(f"Created symlink: {standard_config_dir} -> {stow_config_dir}")
            except Exception as e:
                logger.warning(f"Failed to create additional symlink: {e}")
        
        logger.info("Run 'nvim' after installation to let LazyVim install plugins automatically")
        
        return True
    
    def _get_timestamp(self):
        """Get current timestamp for backup naming"""
        import datetime
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def uninstall_integration(self):
        """Remove Neovim LazyVim configuration"""
        logger.info("Removing Neovim LazyVim configuration...")
        
        os_type = self._detect_os()
        
        # Determine Neovim config directory
        if os_type == "windows":
            nvim_config_dir = Path.home() / "AppData" / "Local" / "nvim"
            nvim_data_dir = Path.home() / "AppData" / "Local" / "nvim-data"
        else:
            nvim_config_dir = Path.home() / ".config" / "nvim"
            nvim_data_dir = Path.home() / ".local" / "share" / "nvim"
        
        # Remove config and data directories
        if os_type == "windows":
            cleanup_script = f"""
            if (Test-Path "{nvim_config_dir}") {{
                Remove-Item -Path "{nvim_config_dir}" -Recurse -Force
            }}
            if (Test-Path "{nvim_data_dir}") {{
                Remove-Item -Path "{nvim_data_dir}" -Recurse -Force
            }}
            Write-Host "LazyVim configuration removed"
            """
        else:
            cleanup_script = f"""
            rm -rf "{nvim_config_dir}"
            rm -rf "{nvim_data_dir}"
            echo "LazyVim configuration removed"
            """
        
        result = self._run_command(cleanup_script)
        
        if result.returncode == 0:
            logger.info("LazyVim configuration removed successfully")
            return True
        else:
            logger.error(f"Configuration removal failed: {result.stderr}")
            return False