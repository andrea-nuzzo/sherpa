# packages/starship/installer.py
from ..base import BaseInstaller
import logging

logger = logging.getLogger(__name__)

class StarshipInstaller(BaseInstaller):
    def install_software(self):
        cmd = "curl -sS https://starship.rs/install.sh | sh"
        self._run_command(cmd)
    
    def is_software_installed(self):
        return self._command_exists("starship")
    
    def uninstall_software(self):
        # Remove starship binary logic
        pass