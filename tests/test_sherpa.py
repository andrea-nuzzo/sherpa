import pytest
from unittest.mock import patch
import sherpa

# ==========================================
# TEST handle_list()
# ==========================================
@pytest.mark.unit
class TestHandleList:
    """Tests for the handle_list function"""

    def test_handle_list_with_packages(self, sample_packages_list, capsys):
        """Test show available packages"""
        # Mock args for the new handle_list function
        from unittest.mock import MagicMock
        args = MagicMock()
        args.category = None
        args.tags = None
        args.all_platforms = False
        
        # ARRANGE & ACT  
        with patch('sherpa.InstallerFactory.get_packages_by_category') as mock_get_packages, \
             patch('sherpa.InstallerFactory.get_category_description') as mock_get_desc, \
             patch('sherpa.InstallerFactory.get_package_metadata') as mock_get_meta:
            
            mock_get_packages.return_value = {'1_shell_and_prompt': sample_packages_list}
            mock_get_desc.return_value = "Shell environments and command line prompts"
            
            # Create mock metadata for each package
            def mock_metadata(package_id):
                mock_meta = MagicMock()
                mock_meta.name = package_id.title()
                mock_meta.summary = f"Mock {package_id} package"
                return mock_meta
            mock_get_meta.side_effect = mock_metadata
            
            sherpa.handle_list(args)
        
        # ASSERT
        captured = capsys.readouterr()
        assert "📦 Available packages by category:" in captured.out
        
        # Verifica che ogni package sia listato
        for package in sample_packages_list:
            assert f"• {package.title()} ({package})" in captured.out
        
        assert "💡 Use 'sherpa install <package>' to install" in captured.out
    
    def test_handle_list_no_packages(self, empty_packages_list, capsys):
        """Test show no available packages"""
        # Mock args for the new handle_list function
        from unittest.mock import MagicMock
        args = MagicMock()
        args.category = None
        args.tags = None
        args.all_platforms = False
        
        # ARRANGE & ACT
        with patch('sherpa.InstallerFactory.get_packages_by_category') as mock_get_packages:
            mock_get_packages.return_value = {}
            sherpa.handle_list(args)
        
        # ASSERT
        captured = capsys.readouterr()
        assert "No packages available for current platform." in captured.out


# ==========================================
# TEST Package Integration
# ==========================================
@pytest.mark.unit 
class TestPackageIntegration:
    """Test that packages can be properly loaded"""
    
    def test_pyenv_package_can_be_loaded(self):
        """Test that pyenv package installer can be created"""
        from packages.factory import InstallerFactory
        
        # ARRANGE & ACT
        factory = InstallerFactory()
        installer = factory.create_installer('pyenv')
        
        # ASSERT
        assert installer is not None
        assert installer.package_name == 'pyenv'
        assert type(installer).__name__ == 'PyenvInstaller'

# ==========================================
# TEST handle_install()
# ==========================================

# ==========================================
# TEST handle_remove()
# ==========================================