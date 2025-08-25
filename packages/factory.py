import importlib
import logging
from pathlib import Path
from .base import BaseInstaller

logger = logging.getLogger(__name__)

class InstallerFactory:
    """Factory class for creating package installers dynamically."""
    
    _package_registry = {
        "ghostty": "GhosttyInstaller",
        "lazydocker": "LazydockerInstaller",
        "lazygit": "LazyGitInstaller",
        "pyenv": "PyenvInstaller",
        "starship": "StarshipInstaller",
        "tmux": "TmuxInstaller",
    }
    
    @classmethod
    def create_installer(cls, package_name: str) -> BaseInstaller:
        """
        Create an installer for the specified package
        
        Args:
            package_name (str): Name of the package to install
        
        Returns:
            BaseInstaller: An instance of the appropriate installer class
        
        Raises:
            ValueError: If the package is not registered
            ImportError: If installer module cannot be loaded
            AttributeError: If installer class is not found
        """
        
        # Validate package exists in our registry
        if package_name not in cls._package_registry:
            available = ", ".join(cls._package_registry.keys())
            error_msg = f"Package '{package_name}' not supported. Available: {available}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # Validate package directory structure exists
            if not cls._validate_package_structure(package_name):
                raise ValueError(f"Invalid package structure for '{package_name}'")
            
            # Dynamic import of installer module
            installer_class = cls._load_installer_class(package_name)
            
            # Create and return installer instance
            installer = installer_class(package_name)
            logger.info(f"Created {installer_class.__name__} for {package_name}")
            return installer
            
        except ImportError as e:
            error_msg = f"Cannot import installer for '{package_name}': {e}"
            logger.error(error_msg)
            raise ImportError(error_msg) from e
        
        except AttributeError as e:
            error_msg = f"Installer class not found for '{package_name}': {e}"
            logger.error(error_msg)
            raise AttributeError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error creating installer for '{package_name}': {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    @classmethod
    def get_available_packages(cls) -> list[str]:
        """
        Get list of all available packages.
        
        Returns:
            list: Sorted list of available package names
        """
        return sorted(cls._package_registry.keys())
    
    @classmethod
    def is_package_supported(cls, package_name: str) -> bool:
        """
        Check if a package is supported by the factory.
        
        Args:
            package_name: Name of the package to check
            
        Returns:
            bool: True if package is supported
        """
        return package_name in cls._package_registry
    
    @classmethod
    def register_package(cls, package_name: str, installer_class_name: str):
        """
        Register a new package with the factory.
        
        Args:
            package_name: Name of the package
            installer_class_name: Name of the installer class
        """
        logger.info(f"Registering package: {package_name} -> {installer_class_name}")
        cls._package_registry[package_name] = installer_class_name
        
    @classmethod
    def auto_discover_packages(cls) -> dict[str, str]:
        """
        Auto-discover packages by scanning the packages directory.
        
        Returns:
            dict: Map of discovered packages to their potential installer classes
        """
        logger.info("Auto-discovering packages...")
        
        packages_dir = Path("packages")
        discovered = {}
        
        if not packages_dir.exists():
            logger.warning("Packages directory not found")
            return discovered
        
        for package_dir in packages_dir.iterdir():
            if package_dir.is_dir() and package_dir.name not in ["__pycache__"]:
                # Skip non-package directories (files like base.py, factory.py)
                if package_dir.name.endswith(".py") or package_dir.name.startswith("__"):
                    continue
                
                installer_file = package_dir / "installer.py"
                config_dir = package_dir / "config"
                
                if installer_file.exists() and config_dir.exists():
                    # Generate expected class name (StarshipInstaller, GitInstaller, etc.)
                    class_name = f"{package_dir.name.title()}Installer"
                    discovered[package_dir.name] = class_name
                    logger.debug(f"Discovered package: {package_dir.name} -> {class_name}")
        
        logger.info(f"Auto-discovered {len(discovered)} packages: {list(discovered.keys())}")
        return discovered
        
    # ==========================================
    # PRIVATE METHODS - Internal implementation
    # ==========================================
    
    @classmethod
    def _validate_package_structure(cls, package_name: str) -> bool:
        """Validate that package has required directory structure."""
        package_dir = Path("packages") / package_name
        installer_file = package_dir / "installer.py"
        config_dir = package_dir / "config"
        
        if not package_dir.exists():
            logger.error(f"Package directory not found: {package_dir}")
            return False
        
        if not installer_file.exists():
            logger.error(f"Installer file not found: {installer_file}")
            return False
        
        if not config_dir.exists():
            logger.error(f"Config directory not found: {config_dir}")
            return False
        
        logger.debug(f"Package structure validated: {package_name}")
        return True
    
    @classmethod
    def _load_installer_class(cls, package_name: str):
        """Load the installer class for a package."""
        expected_class_name = cls._package_registry[package_name]
        
        # Import the installer module
        # packages.starship.installer -> StarshipInstaller
        module_path = f"packages.{package_name}.installer"
        logger.debug(f"Importing module: {module_path}")
        
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            logger.error(f"Failed to import {module_path}: {e}")
            raise
        
        # Get the installer class from the module
        try:
            installer_class = getattr(module, expected_class_name)
        except AttributeError as e:
            logger.error(f"Class '{expected_class_name}' not found in {module_path}")
            logger.info(f"💡 Available classes: {[name for name in dir(module) if not name.startswith('_')]}")
            raise
        
        # Validate it's a subclass of BaseInstaller
        if not issubclass(installer_class, BaseInstaller):
            raise TypeError(f"{expected_class_name} must inherit from BaseInstaller")
        
        logger.debug(f"Loaded installer class: {installer_class}")
        return installer_class
    
    @classmethod
    def get_package_info(cls, package_name: str) -> dict:
        """Get detailed information about a package."""
        if not cls.is_package_supported(package_name):
            return {"error": f"Package '{package_name}' not supported"}
        
        try:
            package_dir = Path("packages") / package_name
            installer_file = package_dir / "installer.py"
            config_dir = package_dir / "config"
            
            # Count config files
            config_files = list(config_dir.rglob("*")) if config_dir.exists() else []
            config_file_count = len([f for f in config_files if f.is_file()])
            
            return {
                "name": package_name,
                "installer_class": cls._package_registry[package_name],
                "installer_exists": installer_file.exists(),
                "config_dir_exists": config_dir.exists(),
                "config_files_count": config_file_count,
                "structure_valid": cls._validate_package_structure(package_name)
            }
        except Exception as e:
            return {"error": f"Error getting package info: {e}"}