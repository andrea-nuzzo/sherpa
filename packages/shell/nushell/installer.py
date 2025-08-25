import logging
from pathlib import Path
from ...base import BaseInstaller

logger = logging.getLogger(__name__)

class NushellInstaller(BaseInstaller):
    """Installer for Nushell - A new type of shell with structured data support"""

    def __init__(self, package_name, category=None):
        super().__init__(package_name, category)
        self.binary_name = "nu"
    
    def install_software(self):
        """Install Nushell using system package manager or GitHub releases"""
        logger.info("Installing Nushell...")
        
        # Try package manager first
        if self._install_via_package_manager():
            return True
        
        # Fallback to GitHub releases
        logger.info("Package manager installation failed or unavailable, trying GitHub releases...")
        return self._install_from_github()
    
    def _install_via_package_manager(self):
        """Install Nushell via system package manager"""
        package_manager, install_cmd = self._get_package_manager()
        
        if not package_manager:
            return False
        
        # Package names vary by distribution
        package_names = {
            "brew": "nushell",
            "apt": "nushell",
            "apt-get": "nushell", 
            "dnf": "nushell",
            "yum": "nushell",
            "pacman": "nushell",
            "winget": "nushell",
            "choco": "nushell"
        }
        
        package_name = package_names.get(package_manager)
        if not package_name:
            logger.debug(f"No package name mapping for {package_manager}")
            return False
        
        full_command = f"{install_cmd} {package_name}"
        logger.info(f"Installing Nushell using: {package_manager}")
        
        result = self._run_command(full_command)
        
        if result.returncode == 0:
            logger.info("Nushell installed successfully via package manager")
            return True
        else:
            logger.warning(f"Package manager installation failed: {result.stderr}")
            return False
    
    def _install_from_github(self):
        """Install Nushell from GitHub releases"""
        os_type = self._detect_os()
        
        # Detect architecture
        arch = self._detect_architecture()
        
        # Build download URL pattern
        if os_type == "macos":
            if arch == "arm64":
                filename = "nu-*-aarch64-darwin.tar.gz"
            else:
                filename = "nu-*-x86_64-darwin.tar.gz"
        elif os_type in ["linux", "debian", "redhat", "arch"]:
            if arch == "arm64":
                filename = "nu-*-aarch64-linux-gnu.tar.gz"
            else:
                filename = "nu-*-x86_64-linux-gnu.tar.gz"
        elif os_type == "windows":
            if arch == "arm64":
                filename = "nu-*-aarch64-pc-windows-msvc.zip"
            else:
                filename = "nu-*-x86_64-pc-windows-msvc.zip"
        else:
            logger.error(f"Unsupported OS for GitHub installation: {os_type}")
            return False
        
        # Download and install
        if os_type == "windows":
            install_script = f"""
            $tempDir = New-TemporaryFile | %{{Remove-Item $_; New-Item -ItemType Directory -Path $_}}
            cd $tempDir
            
            # Get latest release URL
            $latestUrl = (Invoke-RestMethod -Uri "https://api.github.com/repos/nushell/nushell/releases/latest").assets | Where-Object {{$_.name -like "{filename.replace('*', '*')}"}} | Select-Object -First 1 | %{{$_.browser_download_url}}
            
            if (-not $latestUrl) {{
                Write-Error "Could not find download URL for {filename}"
                exit 1
            }}
            
            Write-Host "Downloading: $latestUrl"
            Invoke-WebRequest -Uri $latestUrl -OutFile "nushell.zip"
            
            # Extract
            Expand-Archive -Path "nushell.zip" -DestinationPath "."
            
            # Install to Program Files
            $installPath = "$env:ProgramFiles\\nushell"
            New-Item -ItemType Directory -Path $installPath -Force
            Copy-Item -Path "nu-*\\nu.exe" -Destination "$installPath\\nu.exe" -Force
            
            # Add to PATH
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
            if ($currentPath -notlike "*$installPath*") {{
                [Environment]::SetEnvironmentVariable("Path", "$currentPath;$installPath", "Machine")
            }}
            
            Write-Host "Nushell installed successfully"
            """
        else:
            install_script = f"""
            set -e
            TEMP_DIR=$(mktemp -d)
            cd "$TEMP_DIR"
            
            # Get latest release URL
            LATEST_URL=$(curl -s https://api.github.com/repos/nushell/nushell/releases/latest | grep browser_download_url | grep '{filename.replace('*', '[0-9.]+')}' | head -1 | cut -d '"' -f 4)
            
            if [ -z "$LATEST_URL" ]; then
                echo "Could not find download URL for {filename}"
                exit 1
            fi
            
            echo "Downloading: $LATEST_URL"
            curl -L -o nushell.tar.gz "$LATEST_URL"
            
            # Extract
            tar xzf nushell.tar.gz
            
            # Install binary to /usr/local/bin
            sudo install -Dm755 nu-*/nu /usr/local/bin/nu
            
            # Cleanup
            cd /
            rm -rf "$TEMP_DIR"
            
            echo "Nushell installed successfully"
            """
        
        result = self._run_command(install_script)
        
        if result.returncode == 0:
            logger.info("Nushell installed successfully from GitHub")
            return True
        else:
            logger.error(f"GitHub installation failed: {result.stderr}")
            return False
          
    def uninstall_software(self):
        """Uninstall Nushell"""
        logger.info("Uninstalling Nushell...")
        
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
            "apt": "sudo apt remove -y nushell",
            "apt-get": "sudo apt-get remove -y nushell",
            "dnf": "sudo dnf remove -y nushell",
            "yum": "sudo yum remove -y nushell",
            "pacman": "sudo pacman -R --noconfirm nushell",
            "brew": "brew uninstall nushell",
            "winget": "winget uninstall nushell",
            "choco": "choco uninstall -y nushell"
        }
        
        uninstall_cmd = uninstall_commands.get(package_manager)
        if not uninstall_cmd:
            return False
        
        result = self._run_command(uninstall_cmd)
        
        if result.returncode == 0:
            logger.info("Nushell uninstalled successfully via package manager")
            return True
        else:
            logger.warning(f"Package manager uninstall failed: {result.stderr}")
            return False
    
    def _uninstall_manual(self):
        """Manually remove Nushell binary"""
        os_type = self._detect_os()
        
        if os_type == "windows":
            cleanup_script = """
            # Remove from Program Files
            $installPath = "$env:ProgramFiles\\nushell"
            if (Test-Path $installPath) {
                Remove-Item -Path $installPath -Recurse -Force
            }
            
            # Remove from PATH
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
            $newPath = ($currentPath -split ";") | Where-Object { $_ -ne $installPath } | Join-String -Separator ";"
            [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
            
            Write-Host "Nushell removed manually"
            """
        else:
            cleanup_script = """
            set -e
            
            # Remove binary
            sudo rm -f /usr/local/bin/nu
            sudo rm -f /usr/bin/nu
            
            echo "Nushell removed manually"
            """
        
        result = self._run_command(cleanup_script)
        
        if result.returncode == 0:
            logger.info("Nushell removed manually")
            return True
        else:
            logger.error(f"Manual removal failed: {result.stderr}")
            return False
    
    def is_software_installed(self):
        """Check if Nushell is installed"""
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
        """Setup Nushell integration"""
        logger.info("Setting up Nushell integration...")
        
        # Verify installation
        if self.is_software_installed():
            result = self._run_command("nu --version")
            if result.returncode == 0:
                logger.info(f"Nushell integration complete: {result.stdout.strip()}")
                
                # Check if Nushell config directory exists
                os_type = self._detect_os()
                if os_type == "windows":
                    config_path = Path.home() / "AppData" / "Roaming" / "nushell"
                else:
                    config_path = Path.home() / ".config" / "nushell"
                
                if not config_path.exists():
                    logger.info(f"Creating Nushell config directory: {config_path}")
                    config_path.mkdir(parents=True, exist_ok=True)
                
                logger.info(f"Nushell config will be available at: {config_path}")
                return True
        
        logger.warning("Nushell integration may not be complete")
        return False
    
    def uninstall_integration(self):
        """Remove Nushell integration"""
        logger.info("Removing Nushell integration...")
        logger.info("Note: Nushell config files will remain in ~/.config/nushell/")
        return True