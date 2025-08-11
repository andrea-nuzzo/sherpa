import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

#  Add the project to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ==========================================
# FILESYSTEM & DIRECTORIES
# ==========================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def fake_home_dir(temp_dir):
    """Simulate the user's home directory."""
    home_path = temp_dir / "fake_home"
    home_path.mkdir()
    return home_path


@pytest.fixture
def fake_packages_dir(temp_dir):
    """Create a fake packages/ structure for tests."""
    packages_dir = temp_dir / "packages"
    packages_dir.mkdir()

    # Create a fake starship structure
    starship_dir = packages_dir / "starship"
    starship_dir.mkdir()
    
    # installer.py fake
    installer_file = starship_dir / "installer.py"
    installer_file.write_text("""
from packages.base import BaseInstaller

class StarshipInstaller(BaseInstaller):
    def install_software(self): pass
    def uninstall_software(self): pass  
    def is_software_installed(self): return True
""")
    
    # config directory
    config_dir = starship_dir / "config"
    config_dir.mkdir()
    
    # config file fake
    starship_config = config_dir / ".config" / "starship"
    starship_config.mkdir(parents=True)
    (starship_config / "starship.toml").write_text("[format]\n# Starship config")
    
    return packages_dir


# ==========================================
# COMMON MOCKS
# ==========================================

@pytest.fixture
def mock_subprocess_run():
    """Mock for subprocess.run - avoids executing real commands."""
    with patch('subprocess.run') as mock_run:
        # Default: command always successful
        mock_run.return_value = Mock(
            returncode=0,
            stdout="command successful",
            stderr=""
        )
        yield mock_run


@pytest.fixture  
def mock_command_exists():
    """Mock for shutil.which - checks if command exists."""
    with patch('shutil.which') as mock_which:
        # Default: command always exists
        mock_which.return_value = "/usr/bin/fake_command"
        yield mock_which


@pytest.fixture
def mock_path_home():
    """Mock for Path.home() - avoids using the real home."""
    def _mock_home(fake_home_path):
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = fake_home_path
            yield mock_home
    return _mock_home


# ==========================================
# APPLICATION SPECIFIC MOCKS
# ==========================================

@pytest.fixture
def mock_installer_factory():
    """Mock for InstallerFactory - avoids creating real installers."""
    with patch('packages.factory.InstallerFactory') as mock_factory:
        mock_installer = Mock()
        mock_factory.create_installer.return_value = mock_installer

        # Configure default behaviors
        mock_installer.is_software_installed.return_value = False
        mock_installer.install_software.return_value = True
        mock_installer.install_config.return_value = True
        mock_installer.setup_integration.return_value = True
        
        yield mock_factory, mock_installer


@pytest.fixture
def sample_packages_list():
    """List of example packages for tests."""
    return ["starship", "git", "zsh", "neovim"]


@pytest.fixture
def empty_packages_list():
    """List of packages to test edge cases."""
    return []


# ==========================================
# ENVIRONMENT & OS MOCKS  
# ==========================================

@pytest.fixture
def mock_detect_os():
    """Mock for _detect_os method."""
    def _mock_os(os_name="linux"):
        with patch('packages.base.BaseInstaller._detect_os') as mock_os:
            mock_os.return_value = os_name
            yield mock_os
    return _mock_os


@pytest.fixture
def mock_environment_vars():
    """Mock for environment variables."""
    def _mock_env(**env_vars):
        with patch.dict(os.environ, env_vars):
            yield
    return _mock_env


# ==========================================
# MARKERS CONFIGURATION
# ==========================================

def pytest_configure(config):
    """Configure custom markers for pytest."""
    config.addinivalue_line("markers", "unit: Unit tests (fast)")
    config.addinivalue_line("markers", "integration: Integration tests") 
    config.addinivalue_line("markers", "e2e: End-to-end tests (slow)")
    config.addinivalue_line("markers", "slow: Tests that take >1 second")
    config.addinivalue_line("markers", "external: Requires external dependencies")


# ==========================================
# TEST UTILITIES
# ==========================================

class TestHelpers:
    """Helper methods for tests."""

    @staticmethod
    def create_fake_config_file(path: Path, content: str = "# fake config"):
        """Create a fake config file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path
    
    @staticmethod
    def assert_command_called_with(mock_run, expected_command):
        """Verifies that a command was called with specific arguments"""
        mock_run.assert_called()
        actual_command = mock_run.call_args[0][0]
        assert expected_command in actual_command


@pytest.fixture
def helpers():
    """Provides helper methods for tests"""
    return TestHelpers