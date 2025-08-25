import importlib
import logging
import json
import glob
from pathlib import Path
from .base import BaseInstaller

logger = logging.getLogger(__name__)

class PackageMetadata:
    """Represents package metadata from package.meta.json"""
    
    def __init__(self, metadata_dict: dict, metadata_path: Path):
        self.raw = metadata_dict
        self.path = metadata_path
        
        # Required fields
        self.id = metadata_dict["id"]
        self.name = metadata_dict["name"]
        self.category = metadata_dict["category"]
        self.summary = metadata_dict["summary"]
        self.installer_class = metadata_dict["installer_class"]
        
        # Optional fields with defaults
        self.description = metadata_dict.get("description", self.summary)
        self.version = metadata_dict.get("version", "unknown")
        self.homepage = metadata_dict.get("homepage", "")
        self.repository = metadata_dict.get("repository", "")
        self.requires = metadata_dict.get("requires", [])
        self.conflicts = metadata_dict.get("conflicts", [])
        self.supports = metadata_dict.get("supports", {})
        self.tags = metadata_dict.get("tags", [])
        self.config_files = metadata_dict.get("config_files", [])
        self.post_install = metadata_dict.get("post_install", "")
        
        # Computed fields
        self.package_dir = metadata_path.parent
        self.config_dir = self.package_dir / "config"
        self.installer_path = self.package_dir / "installer.py"
    
    def is_supported_on_current_platform(self) -> bool:
        """Check if package supports current OS/arch"""
        if not self.supports:
            return True  # Assume supported if not specified
        
        import platform
        current_os = platform.system().lower()
        current_arch = platform.machine().lower()
        
        # Map platform names
        os_map = {"darwin": "macos", "linux": "linux", "windows": "windows"}
        arch_map = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x86_64", "amd64": "x86_64"}
        
        current_os = os_map.get(current_os, current_os)
        current_arch = arch_map.get(current_arch, current_arch)
        
        supported_os = self.supports.get("os", [])
        supported_arch = self.supports.get("arch", [])
        
        os_supported = not supported_os or current_os in supported_os
        arch_supported = not supported_arch or current_arch in supported_arch
        
        return os_supported and arch_supported
    
    def matches_tags(self, tag_filter: list) -> bool:
        """Check if package matches any of the provided tags"""
        if not tag_filter:
            return True
        return any(tag in self.tags for tag in tag_filter)

class InstallerFactory:
    """Factory class for creating package installers dynamically with metadata support."""
    
    # Category definitions with descriptions
    _categories = {
        "core": "Bootstrapping and package managers",
        "shell": "Shell environments and command line prompts",
        "terminal": "Terminal emulators and session multiplexers", 
        "editors": "Code editors and development tools",
        "runtimes": "Programming language runtimes and version managers",
        "git": "Git tools and code quality utilities",
        "containers": "Container and containerization tools",
        "k8s": "Kubernetes toolbelt and orchestration",
        "cloud": "Cloud and infrastructure tools",
        "security": "Security and networking utilities",
        "macos": "macOS productivity and automation tools",
        "theme": "Fonts and visual themes",
        "data": "Data tools and extras"
    }
    
    # Package registry with metadata
    _package_registry = {}
    _metadata_cache = {}
    
    @classmethod
    def _discover_packages(cls):
        """Auto-discover all packages from metadata files."""
        if cls._package_registry:
            return cls._package_registry
        
        packages_dir = Path("packages")
        discovered = {}
        metadata_cache = {}
        
        if not packages_dir.exists():
            logger.warning("Packages directory not found")
            return discovered
        
        # Find all package.meta.json files
        metadata_files = list(packages_dir.glob("**/package.meta.json"))
        
        for metadata_file in metadata_files:
            try:
                with open(metadata_file, 'r') as f:
                    metadata_dict = json.load(f)
                
                # Create metadata object
                metadata = PackageMetadata(metadata_dict, metadata_file)
                
                # Validate required structure
                if not metadata.installer_path.exists():
                    logger.warning(f"Missing installer.py for {metadata.id}: {metadata.installer_path}")
                    continue
                
                if not metadata.config_dir.exists():
                    logger.warning(f"Missing config directory for {metadata.id}: {metadata.config_dir}")
                    continue
                
                # Validate category
                if metadata.category not in cls._categories:
                    logger.warning(f"Unknown category '{metadata.category}' for {metadata.id}")
                    continue
                
                # Store in registries
                discovered[metadata.id] = {
                    "category": metadata.category,
                    "class_name": metadata.installer_class,
                    "path": f"{metadata.category}.{metadata.id}",
                    "metadata": metadata
                }
                metadata_cache[metadata.id] = metadata
                
                logger.debug(f"Discovered {metadata.id} in {metadata.category} -> {metadata.installer_class}")
                
            except Exception as e:
                logger.error(f"Error loading metadata from {metadata_file}: {e}")
                continue
        
        cls._package_registry = discovered
        cls._metadata_cache = metadata_cache
        logger.info(f"Auto-discovered {len(discovered)} packages across {len(cls._categories)} categories")
        return discovered
    
    @classmethod
    def create_installer(cls, package_id: str) -> BaseInstaller:
        """
        Create an installer for the specified package
        
        Args:
            package_id (str): ID of the package to install
        
        Returns:
            BaseInstaller: An instance of the appropriate installer class
        """
        
        # Discover packages if not already done
        registry = cls._discover_packages()
        
        # Validate package exists in our registry
        if package_id not in registry:
            available = ", ".join(sorted(registry.keys()))
            error_msg = f"Package '{package_id}' not found. Available: {available}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        package_info = registry[package_id]
        metadata = package_info["metadata"]
        
        try:
            # Check platform support
            if not metadata.is_supported_on_current_platform():
                supported = metadata.supports
                logger.warning(f"Package '{package_id}' may not support current platform. Supported: {supported}")
            
            # Dynamic import of installer module
            installer_class = cls._load_installer_class(package_id, package_info)
            
            # Create and return installer instance
            category = package_info["category"]
            installer = installer_class(package_id, category)
            logger.info(f"Created {installer_class.__name__} for {package_id}")
            return installer
            
        except ImportError as e:
            error_msg = f"Cannot import installer for '{package_id}': {e}"
            logger.error(error_msg)
            raise ImportError(error_msg) from e
        
        except AttributeError as e:
            error_msg = f"Installer class not found for '{package_id}': {e}"
            logger.error(error_msg)
            raise AttributeError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error creating installer for '{package_id}': {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    @classmethod
    def get_available_packages(cls, platform_filter: bool = True) -> list[str]:
        """Get list of all available packages, optionally filtered by platform support."""
        cls._discover_packages()
        packages = []
        
        for package_id, metadata in cls._metadata_cache.items():
            if not platform_filter or metadata.is_supported_on_current_platform():
                packages.append(package_id)
        
        return sorted(packages)
    
    @classmethod 
    def get_packages_by_category(cls, platform_filter: bool = True) -> dict[str, list[str]]:
        """Get packages organized by category, optionally filtered by platform support."""
        cls._discover_packages()
        by_category = {}
        
        for package_id, metadata in cls._metadata_cache.items():
            if platform_filter and not metadata.is_supported_on_current_platform():
                continue
            
            category = metadata.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(package_id)
        
        # Sort packages within each category
        for category in by_category:
            by_category[category].sort()
        
        return by_category
    
    @classmethod
    def get_package_metadata(cls, package_id: str) -> PackageMetadata:
        """Get metadata for a specific package."""
        cls._discover_packages()
        if package_id not in cls._metadata_cache:
            raise ValueError(f"Package '{package_id}' not found")
        return cls._metadata_cache[package_id]
    
    @classmethod
    def search_packages(cls, query: str = "", category: str = "", tags: list = None, platform_filter: bool = True) -> list[PackageMetadata]:
        """Search packages by query, category, and/or tags."""
        cls._discover_packages()
        results = []
        
        for package_id, metadata in cls._metadata_cache.items():
            # Platform filter
            if platform_filter and not metadata.is_supported_on_current_platform():
                continue
            
            # Category filter
            if category and metadata.category != category:
                continue
            
            # Tag filter
            if tags and not metadata.matches_tags(tags):
                continue
            
            # Query filter (search in name, summary, description, tags)
            if query:
                query_lower = query.lower()
                searchable_text = f"{metadata.name} {metadata.summary} {metadata.description} {' '.join(metadata.tags)}".lower()
                if query_lower not in searchable_text:
                    continue
            
            results.append(metadata)
        
        return sorted(results, key=lambda x: x.name)
    
    @classmethod
    def validate_dependencies_and_conflicts(cls, package_id: str, installed_packages: list = None) -> dict:
        """Validate dependencies and conflicts for a package installation."""
        if installed_packages is None:
            installed_packages = []
        
        metadata = cls.get_package_metadata(package_id)
        issues = {
            "missing_dependencies": [],
            "conflicts": [],
            "warnings": []
        }
        
        # Check dependencies
        for dependency in metadata.requires:
            if dependency not in installed_packages:
                issues["missing_dependencies"].append(dependency)
        
        # Check conflicts
        for conflict in metadata.conflicts:
            if conflict in installed_packages:
                issues["conflicts"].append(conflict)
        
        # Platform warnings
        if not metadata.is_supported_on_current_platform():
            issues["warnings"].append(f"Package may not support current platform: {metadata.supports}")
        
        return issues
    
    @classmethod
    def get_category_description(cls, category_name: str) -> str:
        """Get description for a category."""
        return cls._categories.get(category_name, "Unknown category")
    
    @classmethod
    def get_all_categories(cls) -> dict[str, str]:
        """Get all categories with their descriptions."""
        return cls._categories.copy()
    
    @classmethod
    def is_package_supported(cls, package_id: str) -> bool:
        """Check if a package is supported by the factory."""
        registry = cls._discover_packages()
        return package_id in registry
    
    @classmethod
    def get_package_category(cls, package_id: str) -> str:
        """Get the category of a specific package."""
        try:
            metadata = cls.get_package_metadata(package_id)
            return metadata.category
        except ValueError:
            return None
        
    # ==========================================
    # PRIVATE METHODS - Internal implementation
    # ==========================================
    
    @classmethod
    def _load_installer_class(cls, package_id: str, package_info: dict):
        """Load the installer class for a package."""
        category = package_info["category"]
        expected_class_name = package_info["class_name"]
        
        # Import the installer module
        module_path = f"packages.{category}.{package_id}.installer"
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