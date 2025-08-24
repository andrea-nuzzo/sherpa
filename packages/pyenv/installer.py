import logging
import os
import re
from pathlib import Path
from ..base import BaseInstaller

logger = logging.getLogger(__name__)

class PyenvInstaller(BaseInstaller):
    """Installer for pyenv Python version manager"""

    def __init__(self, package_name):
        super().__init__(package_name)
        self.binary_name = "pyenv"
        self.pyenv_root = Path.home() / ".pyenv"
    
    # ==========================================
    # ABSTRACT METHODS - Software installation
    # ==========================================

    def install_software(self):
        """Install pyenv using the official installation script"""
        logger.info("Installing pyenv...")
        
        os_type = self._detect_os()
        
        if os_type in ["linux", "macos", "debian", "redhat", "arch"]:
            # Use the official pyenv installer
            cmd = "curl https://pyenv.run | bash"
            result = self._run_command(cmd)
            
            if result.returncode == 0:
                logger.info("Pyenv installed successfully")
                
                # Setup shell integration
                if self._setup_shell_integration():
                    logger.info("Shell integration configured")
                
                # Ask user which Python version to install
                if self._install_python_version():
                    logger.info("Python version installed successfully")
                
                return True
            else:
                logger.error(f"Pyenv installation failed: {result.stderr}")
                return False
        elif os_type == "windows":
            logger.error("Windows is not supported by pyenv. Consider using pyenv-win instead.")
            return False
        else:
            logger.error(f"Unsupported OS: {os_type}")
            return False
          
    def uninstall_software(self):
        """Uninstall pyenv and remove shell integration"""
        logger.info("Uninstalling pyenv...")
        
        try:
            # Critical safety check: ensure Python will still be available after removal
            if not self._check_python_availability_after_removal():
                logger.error("❌ Cannot remove pyenv: no alternative Python installation found!")
                logger.info("💡 Pyenv appears to be the only Python on your system.")
                logger.info("💡 Install a system Python first, then try removing pyenv again:")
                
                os_type = self._detect_os()
                if os_type == "macos":
                    logger.info("   • brew install python")
                    logger.info("   • Or install from python.org")
                elif os_type in ["debian", "ubuntu"]:
                    logger.info("   • sudo apt install python3")
                elif os_type in ["redhat", "fedora", "centos"]:
                    logger.info("   • sudo dnf install python3")
                elif os_type == "arch":
                    logger.info("   • sudo pacman -S python")
                else:
                    logger.info("   • Install Python from python.org or your package manager")
                
                return False
            
            # Remove shell integration first
            self._remove_shell_integration()
            
            # Detect installation method and uninstall accordingly
            installation_method = self._detect_installation_method()
            
            if installation_method == "homebrew":
                logger.info("Detected Homebrew installation, removing with brew...")
                result = self._run_command("brew uninstall pyenv")
                if result.returncode != 0:
                    logger.error(f"Homebrew uninstall failed: {result.stderr}")
                    return False
                logger.info("Pyenv uninstalled via Homebrew")
            
            elif installation_method == "script":
                logger.info("Detected script installation, removing manually...")
                # For script installations, pyenv is typically in ~/.pyenv
                if self.pyenv_root.exists():
                    import shutil
                    shutil.rmtree(self.pyenv_root)
                    logger.info("Pyenv directory removed")
                else:
                    logger.warning("Pyenv directory not found, may already be removed")
            
            elif installation_method == "package_manager":
                logger.info("Detected package manager installation...")
                package_manager, _ = self._get_package_manager()
                if package_manager == "apt":
                    result = self._run_command("sudo apt remove -y pyenv")
                elif package_manager == "yum" or package_manager == "dnf":
                    result = self._run_command(f"sudo {package_manager} remove -y pyenv")
                elif package_manager == "pacman":
                    result = self._run_command("sudo pacman -R --noconfirm pyenv")
                else:
                    logger.warning(f"Unsupported package manager: {package_manager}")
                    return False
                    
                if result.returncode != 0:
                    logger.error(f"Package manager uninstall failed: {result.stderr}")
                    return False
                logger.info(f"Pyenv uninstalled via {package_manager}")
            
            else:
                logger.warning("Could not detect installation method")
                logger.info("💡 You may need to manually uninstall pyenv")
                # Still remove the ~/.pyenv directory if it exists
                if self.pyenv_root.exists():
                    import shutil
                    shutil.rmtree(self.pyenv_root)
                    logger.info("Pyenv data directory removed")
            
            # Always remove the data directory if it still exists
            if self.pyenv_root.exists():
                import shutil
                shutil.rmtree(self.pyenv_root)
                logger.info("Pyenv data directory removed")
            
            logger.info("Pyenv uninstalled successfully")
            logger.info("💡 Restart your shell or source your shell config to complete removal")
            return True
            
        except Exception as e:
            logger.error(f"Pyenv uninstallation failed: {e}")
            return False
    
    def is_software_installed(self):
        """Check if pyenv is installed"""
        return self._command_exists(self.binary_name) or self.pyenv_root.exists()
    
    # ==========================================
    # PYTHON VERSION MANAGEMENT
    # ==========================================
    
    def _install_python_version(self):
        """Prompt user for Python version and install it"""
        logger.info("\n🐍 Python Version Setup")
        logger.info("What Python version would you like to install?")
        
        # Show available Python versions
        available_versions = self._get_available_python_versions()
        
        if not available_versions:
            logger.warning("Could not fetch available Python versions")
            logger.info("💡 You can install a Python version later with: pyenv install <version>")
            return True
        
        # Show recent stable versions
        recent_versions = self._filter_recent_stable_versions(available_versions)
        
        logger.info("Recent stable versions:")
        for i, version in enumerate(recent_versions[:5], 1):
            logger.info(f"  {i}. Python {version}")
        
        logger.info(f"  {len(recent_versions[:5]) + 1}. Skip (install later)")
        logger.info("  Or enter a specific version (e.g., 3.11.5)")
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if not choice or choice == str(len(recent_versions[:5]) + 1):
                logger.info("Skipping Python installation")
                logger.info("💡 Install a Python version later with: pyenv install <version>")
                return True
            
            # Check if it's a number selection
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(recent_versions[:5]):
                    selected_version = recent_versions[choice_idx]
                else:
                    logger.error("Invalid choice")
                    return False
            else:
                # User entered a specific version
                selected_version = choice
                
                # Validate version format
                if not re.match(r'^\d+\.\d+(\.\d+)?$', selected_version):
                    logger.error("Invalid version format. Expected format: x.y.z")
                    return False
            
            return self._install_and_set_python_version(selected_version)
            
        except KeyboardInterrupt:
            logger.info("\nSkipping Python installation")
            return True
        except Exception as e:
            logger.error(f"Error during version selection: {e}")
            return False
    
    def _get_available_python_versions(self):
        """Get list of available Python versions from pyenv"""
        try:
            # First ensure pyenv is in PATH for this session
            pyenv_bin = self.pyenv_root / "bin" / "pyenv"
            if not pyenv_bin.exists():
                return []
            
            cmd = f"{pyenv_bin} install --list"
            result = self._run_command(cmd)
            
            if result.returncode != 0:
                return []
            
            # Parse versions from output
            versions = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                # Match Python versions (3.x.x format)
                if re.match(r'^\d+\.\d+\.\d+$', line):
                    versions.append(line)
            
            return sorted(versions, key=lambda x: [int(i) for i in x.split('.')], reverse=True)
            
        except Exception as e:
            logger.debug(f"Failed to get available versions: {e}")
            return []
    
    def _filter_recent_stable_versions(self, versions):
        """Filter to get recent stable versions (3.8+, latest patches)"""
        recent_stable = []
        seen_minor = set()
        
        for version in versions:
            major, minor, patch = version.split('.')
            major, minor = int(major), int(minor)
            
            # Only Python 3.8+ and skip pre-release versions
            if major == 3 and minor >= 8:
                minor_version = f"{major}.{minor}"
                if minor_version not in seen_minor:
                    recent_stable.append(version)
                    seen_minor.add(minor_version)
                    
                    # Stop after getting 6 different minor versions
                    if len(recent_stable) >= 6:
                        break
        
        return recent_stable
    
    def _install_and_set_python_version(self, version):
        """Install the specified Python version and set it as global default"""
        logger.info(f"Installing Python {version}...")
        
        try:
            pyenv_bin = self.pyenv_root / "bin" / "pyenv"
            
            # Install the Python version
            cmd = f"{pyenv_bin} install {version}"
            result = self._run_command(cmd)
            
            if result.returncode != 0:
                logger.error(f"Failed to install Python {version}: {result.stderr}")
                return False
            
            logger.info(f"Python {version} installed successfully")
            
            # Set as global default
            cmd = f"{pyenv_bin} global {version}"
            result = self._run_command(cmd)
            
            if result.returncode == 0:
                logger.info(f"Set Python {version} as global default")
                logger.info("💡 Restart your shell to use the new Python version")
                return True
            else:
                logger.warning(f"Failed to set Python {version} as global default")
                return True  # Installation succeeded, setting global failed
                
        except Exception as e:
            logger.error(f"Failed to install Python version: {e}")
            return False
    
    # ==========================================
    # INTEGRATION SETUP - Shell configuration
    # ==========================================
    
    def setup_integration(self):
        """Setup shell integration for pyenv (alias for _setup_shell_integration)"""
        return self._setup_shell_integration()
    
    def uninstall_integration(self):
        """Remove shell integration for pyenv (alias for _remove_shell_integration)"""
        return self._remove_shell_integration()
    
    # ==========================================
    # SHELL INTEGRATION - Internal methods
    # ==========================================
    
    def _setup_shell_integration(self):
        """Setup shell integration for pyenv"""
        logger.info("Setting up shell integration...")
        
        current_shell = self._detect_current_shell()
        logger.debug(f"Detected shell: {current_shell}")
        
        if current_shell == "bash":
            return self._setup_bash_integration()
        elif current_shell == "zsh":
            return self._setup_zsh_integration()
        else:
            logger.warning(f"Unsupported shell for auto-config: {current_shell}")
            logger.info("💡 Manually add pyenv to your shell config")
            return True
    
    def _remove_shell_integration(self):
        """Remove shell integration for pyenv"""
        logger.info("Removing shell integration...")
        
        current_shell = self._detect_current_shell()
        
        if current_shell == "bash":
            return self._remove_bash_integration()
        elif current_shell == "zsh":
            return self._remove_zsh_integration()
        else:
            return True
    
    def _setup_bash_integration(self):
        """Add pyenv to ~/.bashrc"""
        bashrc_path = self.home_dir / '.bashrc'
        
        pyenv_config = [
            '# Pyenv configuration',
            'export PYENV_ROOT="$HOME/.pyenv"',
            'export PATH="$PYENV_ROOT/bin:$PATH"',
            'eval "$(pyenv init -)"'
        ]
        
        try:
            # Check if already configured
            if bashrc_path.exists():
                content = bashrc_path.read_text()
                if 'pyenv init' in content:
                    logger.info("Bash integration already configured")
                    return True
            
            # Add to .bashrc
            with bashrc_path.open('a') as f:
                f.write('\n' + '\n'.join(pyenv_config) + '\n')
            
            logger.info("Added pyenv to ~/.bashrc")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup bash integration: {e}")
            return False
    
    def _setup_zsh_integration(self):
        """Add pyenv to ~/.zshrc"""
        zshrc_path = self.home_dir / '.zshrc'
        
        pyenv_config = [
            '# Pyenv configuration',
            'export PYENV_ROOT="$HOME/.pyenv"',
            'export PATH="$PYENV_ROOT/bin:$PATH"',
            'eval "$(pyenv init -)"'
        ]
        
        try:
            # Check if already configured
            if zshrc_path.exists():
                content = zshrc_path.read_text()
                if 'pyenv init' in content:
                    logger.info("Zsh integration already configured")
                    return True
            
            # Add to .zshrc
            with zshrc_path.open('a') as f:
                f.write('\n' + '\n'.join(pyenv_config) + '\n')
            
            logger.info("Added pyenv to ~/.zshrc")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup zsh integration: {e}")
            return False
    
    def _remove_bash_integration(self):
        """Remove bash integration for pyenv"""
        bashrc_path = self.home_dir / '.bashrc'

        if not bashrc_path.exists():
            return True

        try:
            content = bashrc_path.read_text()
            
            # Remove pyenv-related lines
            lines = content.split('\n')
            filtered_lines = []
            skip_next = False
            
            for line in lines:
                if 'pyenv' in line.lower() and any(x in line for x in ['export', 'eval', '#']):
                    continue
                filtered_lines.append(line)
            
            bashrc_path.write_text('\n'.join(filtered_lines))
            logger.info("Removed pyenv from ~/.bashrc")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove bash integration: {e}")
            return False
    
    def _remove_zsh_integration(self):
        """Remove zsh integration for pyenv"""
        zshrc_path = self.home_dir / '.zshrc'

        if not zshrc_path.exists():
            return True

        try:
            content = zshrc_path.read_text()
            
            # Remove pyenv-related lines
            lines = content.split('\n')
            filtered_lines = []
            
            for line in lines:
                if 'pyenv' in line.lower() and any(x in line for x in ['export', 'eval', '#']):
                    continue
                filtered_lines.append(line)
            
            zshrc_path.write_text('\n'.join(filtered_lines))
            logger.info("Removed pyenv from ~/.zshrc")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove zsh integration: {e}")
            return False
    
    def _check_python_availability_after_removal(self):
        """Check if Python will still be available after removing pyenv"""
        logger.info("🔍 Checking for functional Python installations...")
        
        viable_pythons = []
        
        # Step 1: Find potential Python executables
        python_candidates = self._find_python_candidates()
        
        if not python_candidates:
            logger.warning("❌ No Python executables found")
            return False
        
        # Step 2: Test each candidate for functionality
        for python_path, source in python_candidates:
            logger.info(f"🧪 Testing Python at {python_path} (from {source})")
            
            # Test 1: Basic functionality
            if not self._test_python_functionality(python_path):
                logger.warning(f"❌ {python_path}: Basic functionality test failed")
                continue
            
            # Test 2: Check if it's a macOS stub
            if self._is_macos_python_stub(python_path):
                logger.warning(f"❌ {python_path}: Detected as macOS Python stub")
                continue
            
            # Test 3: Check pip availability
            has_pip = self._test_python_pip(python_path)
            
            # Add to viable list
            viable_pythons.append({
                'path': python_path,
                'source': source,
                'has_pip': has_pip,
                'version': self._get_python_version(python_path)
            })
            
            logger.info(f"✅ {python_path}: Functional Python found (pip: {'✅' if has_pip else '❌'})")
        
        # Step 3: Evaluate results
        if not viable_pythons:
            logger.error("❌ No functional Python installations found!")
            logger.info("💡 All detected Python installations are either:")
            logger.info("   • macOS stubs that require Xcode Command Line Tools")
            logger.info("   • Broken or incomplete installations")
            logger.info("   • Missing essential functionality")
            return False
        
        # Step 4: Report findings and determine if safe to proceed
        logger.info(f"✅ Found {len(viable_pythons)} functional Python installation(s):")
        for python in viable_pythons:
            pip_status = "with pip" if python['has_pip'] else "without pip"
            logger.info(f"   • {python['path']} ({python['version']}, {pip_status})")
        
        # If we have at least one functional Python with pip, it's safe
        pythons_with_pip = [p for p in viable_pythons if p['has_pip']]
        if pythons_with_pip:
            logger.info("✅ Safe to remove pyenv - functional Python with pip available")
            return True
        
        # If we only have Pythons without pip, ask user
        logger.warning("⚠️  Found Python installations but none have pip installed")
        logger.info("💡 You may want to install pip first:")
        for python in viable_pythons:
            logger.info(f"   curl https://bootstrap.pypa.io/get-pip.py | {python['path']}")
        
        return self._confirm_removal_without_pip(viable_pythons)
    
    def _find_python_candidates(self):
        """Find all potential Python executable candidates"""
        candidates = []
        
        # Direct paths to check
        direct_paths = [
            "/usr/bin/python3",
            "/usr/bin/python",
            "/usr/local/bin/python3", 
            "/usr/local/bin/python",
            "/opt/homebrew/bin/python3",
            "/opt/homebrew/bin/python3.13",
            "/opt/homebrew/bin/python3.12",
            "/opt/homebrew/bin/python3.11",
            "/opt/homebrew/bin/python3.10",
        ]
        
        for path in direct_paths:
            if Path(path).exists():
                source = "system" if path.startswith("/usr/") else "homebrew" if "homebrew" in path else "local"
                candidates.append((path, source))
        
        # Wildcard paths (macOS system Python, Python.org installations)
        wildcard_paths = [
            ("/System/Library/Frameworks/Python.framework/Versions/3.*/bin/python3", "system"),
            ("/Library/Frameworks/Python.framework/Versions/3.*/bin/python3", "python.org"),
            ("/Applications/Python*/Python*/bin/python3", "python.org")
        ]
        
        import glob
        for pattern, source in wildcard_paths:
            matching_paths = glob.glob(pattern)
            for path in matching_paths:
                if Path(path).exists():
                    candidates.append((path, source))
        
        # Check Homebrew installations
        if self._command_exists("brew"):
            homebrew_versions = ["3.13", "3.12", "3.11", "3.10", "3.9"]
            for version in homebrew_versions:
                result = self._run_command(f"brew --prefix python@{version} 2>/dev/null", capture_output=True)
                if result.returncode == 0 and result.stdout.strip():
                    python_path = result.stdout.strip() + "/bin/python3"
                    if Path(python_path).exists():
                        candidates.append((python_path, f"homebrew@{version}"))
        
        # PATH-based discovery (exclude pyenv)
        current_path = os.environ.get('PATH', '')
        clean_path = ':'.join([p for p in current_path.split(':') 
                              if '.pyenv' not in p and 'pyenv' not in p.lower()])
        
        for cmd in ['python3', 'python']:
            result = self._run_command(f"PATH='{clean_path}' which {cmd} 2>/dev/null", capture_output=True)
            if result.returncode == 0 and result.stdout.strip():
                python_path = result.stdout.strip()
                if '.pyenv' not in python_path:
                    # Avoid duplicates
                    if not any(python_path == candidate[0] for candidate in candidates):
                        candidates.append((python_path, "PATH"))
        
        return candidates
    
    def _test_python_functionality(self, python_path):
        """Test if Python executable is functional"""
        try:
            # Test 1: Basic Python execution
            result = self._run_command(f'"{python_path}" -c "import sys; print(sys.version)" 2>/dev/null', capture_output=True)
            if result.returncode != 0:
                return False
            
            # Test 2: Can import standard library modules
            test_imports = ['os', 'sys', 'json', 'urllib', 'ssl']
            for module in test_imports:
                result = self._run_command(f'"{python_path}" -c "import {module}" 2>/dev/null', capture_output=True)
                if result.returncode != 0:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _is_macos_python_stub(self, python_path):
        """Check if this is a macOS Python stub that requires Xcode tools"""
        try:
            # Run a command that would trigger the stub behavior
            result = self._run_command(f'"{python_path}" -c "import ssl" 2>&1', capture_output=True)
            
            # Check for common stub messages
            stub_indicators = [
                "xcode-select --install",
                "command line tools",
                "developer tools", 
                "install the command line developer tools",
                "xcrun: error"
            ]
            
            output = (result.stdout + result.stderr).lower()
            return any(indicator in output for indicator in stub_indicators)
            
        except Exception:
            return False
    
    def _test_python_pip(self, python_path):
        """Test if pip is available for this Python"""
        try:
            # Try importing pip
            result = self._run_command(f'"{python_path}" -c "import pip" 2>/dev/null', capture_output=True)
            if result.returncode == 0:
                return True
            
            # Try running pip as module
            result = self._run_command(f'"{python_path}" -m pip --version 2>/dev/null', capture_output=True)
            if result.returncode == 0:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _get_python_version(self, python_path):
        """Get Python version string"""
        try:
            result = self._run_command(f'"{python_path}" --version 2>&1', capture_output=True)
            if result.returncode == 0:
                return result.stdout.strip() or result.stderr.strip()
            return "unknown"
        except Exception:
            return "unknown"
    
    def _confirm_removal_without_pip(self, viable_pythons):
        """Ask user confirmation when Python exists but without pip"""
        try:
            logger.warning("⚠️  Pyenv removal requires confirmation:")
            logger.info("Found Python installations without pip. You can:")
            logger.info("1. Install pip first (recommended)")
            logger.info("2. Proceed anyway (you'll need to manually install pip later)")
            logger.info("3. Cancel removal")
            
            choice = input("\nProceed with pyenv removal? (y/N): ").strip().lower()
            
            if choice in ['y', 'yes']:
                logger.info("✅ User confirmed removal despite missing pip")
                return True
            else:
                logger.info("❌ User cancelled removal")
                return False
                
        except KeyboardInterrupt:
            logger.info("\n❌ Removal cancelled by user")
            return False
        except Exception:
            # If we can't get user input, be conservative
            logger.warning("❌ Cannot get user confirmation, aborting removal")
            return False
    
    def _detect_installation_method(self):
        """Detect how pyenv was installed"""
        # Check if installed via Homebrew
        if self._command_exists("brew"):
            result = self._run_command("brew list pyenv", capture_output=True)
            if result.returncode == 0:
                return "homebrew"
        
        # Check if installed via package manager
        package_manager, _ = self._get_package_manager()
        if package_manager:
            if package_manager in ["apt", "apt-get"]:
                result = self._run_command("dpkg -l | grep -i pyenv", capture_output=True)
                if result.returncode == 0 and result.stdout.strip():
                    return "package_manager"
            elif package_manager in ["dnf", "yum"]:
                result = self._run_command("rpm -qa | grep -i pyenv", capture_output=True)
                if result.returncode == 0 and result.stdout.strip():
                    return "package_manager"
            elif package_manager == "pacman":
                result = self._run_command("pacman -Q pyenv", capture_output=True)
                if result.returncode == 0:
                    return "package_manager"
        
        # Check if installed via script (binary in ~/.pyenv/bin)
        pyenv_script_bin = self.pyenv_root / "bin" / "pyenv"
        if pyenv_script_bin.exists():
            return "script"
        
        # Check if pyenv exists in ~/.pyenv (script installation remnant)
        if self.pyenv_root.exists():
            return "script"
        
        return "unknown"
    
    def _detect_current_shell(self):
        """Detect current shell"""
        import os
        
        shell_path = os.environ.get('SHELL', '')
        if shell_path:
            shell_name = Path(shell_path).name
            if shell_name in ['bash', 'zsh', 'fish']:
                return shell_name
        
        # Fallback based on OS
        os_type = self._detect_os()
        if os_type in ['debian', 'redhat', 'arch', 'linux']:
            return 'bash'
        elif os_type == 'macos':
            return 'zsh'
        
        return 'unknown'