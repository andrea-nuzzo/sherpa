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
        # ARRANGE & ACT
        with patch('sherpa.get_available_packages', return_value=sample_packages_list):
            sherpa.handle_list()
        
        # ASSERT
        captured = capsys.readouterr()
        assert "📦 Available packages:" in captured.out
        
        # Verifica che ogni package sia listato
        for package in sample_packages_list:
            assert f"• {package}" in captured.out
        
        assert "💡 Use 'sherpa install <package>' to install" in captured.out
    
    def test_handle_list_no_packages(self, empty_packages_list, capsys):
        """Test show no available packages"""
        # ARRANGE & ACT
        with patch('sherpa.get_available_packages', return_value=empty_packages_list):
            sherpa.handle_list()
        
        # ASSERT
        captured = capsys.readouterr()
        assert "No packages available." in captured.out
        assert "Create packages in: packages/<name>/installer.py + packages/<name>/config/" in captured.out


# ==========================================
# TEST handle_install()
# ==========================================

# ==========================================
# TEST handle_remove()
# ==========================================