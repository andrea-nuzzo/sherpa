import os
import sys
import argparse
import logging
from pathlib import Path

from packages.factory import InstallerFactory


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_parser():
    """Create and return the argument parser for the sherpa manager."""
    parser = argparse.ArgumentParser(
        prog="sherpa",
        description="🚀 Sherpa Manage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            %(prog)s status                   # Show status package
            %(prog)s clean --all              # Remove all configurations and packages

            Available packages: starship
        """,
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands", 
        metavar="COMMAND"
    )
    
    list_parser = subparsers.add_parser(
        "list",
        help="%(prog)s list ------------------- Show available packages"
    )
    list_parser.add_argument(
        "--category", "-c",
        help="Filter by category (e.g., '1_shell_and_prompt')"
    )
    list_parser.add_argument(
        "--tags", "-t",
        nargs="+",
        help="Filter by tags (e.g., 'tui git')"
    )
    list_parser.add_argument(
        "--all-platforms",
        action="store_true",
        help="Show packages for all platforms (not just current)"
    )
    
    install_parser = subparsers.add_parser(
        "install",
        help="%(prog)s install <name package> - Install specified package"
    )
    
    install_parser.add_argument(
        "package",
        help="Package name to install (e.g., starship)"
    )

    remove_parser = subparsers.add_parser(
        "remove",
        help="%(prog)s remove <name package> - Remove specified package"
    )

    remove_parser.add_argument(
        "package",
        help="Package name to uninstall (e.g., starship)"
    )
    
    info_parser = subparsers.add_parser(
        "info",
        help="%(prog)s info <package> - Show detailed package information"
    )
    info_parser.add_argument(
        "package",
        help="Package name to show info for"
    )
    
    search_parser = subparsers.add_parser(
        "search",
        help="%(prog)s search <query> - Search packages"
    )
    search_parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Search query (searches name, summary, description, tags)"
    )
    search_parser.add_argument(
        "--category", "-c",
        help="Filter by category"
    )
    search_parser.add_argument(
        "--tags", "-t",
        nargs="+",
        help="Filter by tags"
    )

    return parser

def handle_info(args):
    """Handle the info command - show detailed package information."""
    try:
        metadata = InstallerFactory.get_package_metadata(args.package)
        
        category_display = metadata.category.replace('_', ' ').title().replace(' And ', ' & ')
        tags_display = ', '.join(metadata.tags) if metadata.tags else 'none'
        requires_display = ', '.join(metadata.requires) if metadata.requires else 'none'
        conflicts_display = ', '.join(metadata.conflicts) if metadata.conflicts else 'none'
        
        print(f"📦 {metadata.name} ({metadata.id})")
        print(f"Category: {category_display}")
        print(f"Summary: {metadata.summary}")
        print(f"Description: {metadata.description}")
        print(f"Version: {metadata.version}")
        print(f"Tags: {tags_display}")
        print(f"Requires: {requires_display}")
        print(f"Conflicts: {conflicts_display}")
        
        if metadata.homepage:
            print(f"Homepage: {metadata.homepage}")
        if metadata.repository:
            print(f"Repository: {metadata.repository}")
        
        # Platform support
        if metadata.supports:
            supported_os = ', '.join(metadata.supports.get('os', [])) or 'all'
            supported_arch = ', '.join(metadata.supports.get('arch', [])) or 'all'
            print(f"Supported OS: {supported_os}")
            print(f"Supported Architecture: {supported_arch}")
        
        # Config files
        if metadata.config_files:
            print(f"Config files: {', '.join(metadata.config_files)}")
        
        # Post-install message
        if metadata.post_install:
            print(f"\n💡 {metadata.post_install}")
            
    except ValueError as e:
        print(f"Package not found: {e}")
        available_packages = InstallerFactory.get_available_packages()
        print(f"Available packages: {', '.join(available_packages)}")
    except Exception as e:
        logger.error(f"Error getting package info: {e}")
        print("Error retrieving package information.")

def handle_search(args):
    """Handle the search command - search packages by query, category, and tags."""
    try:
        results = InstallerFactory.search_packages(
            query=args.query,
            category=args.category,
            tags=args.tags
        )
        
        if results:
            print(f"🔍 Found {len(results)} packages matching criteria:\n")
            for metadata in results:
                category_display = metadata.category.replace('_', ' ').title().replace(' And ', ' & ')
                tags_display = ', '.join(metadata.tags) if metadata.tags else 'none'
                print(f"• {metadata.name} ({metadata.id})")
                print(f"  Category: {category_display}")
                print(f"  Summary: {metadata.summary}")
                print(f"  Tags: {tags_display}")
                print()
        else:
            print("No packages found matching criteria.")
            
    except Exception as e:
        logger.error(f"Error searching packages: {e}")
        print("Error searching packages.")

def handle_list(args):
    """Handle the list command - show available packages with filtering options."""
    try:
        platform_filter = not args.all_platforms
        
        if args.category or args.tags:
            # Use search functionality for filtering
            results = InstallerFactory.search_packages(
                category=args.category,
                tags=args.tags,
                platform_filter=platform_filter
            )
            
            if results:
                print(f"📦 Found {len(results)} packages:\n")
                for metadata in results:
                    category_display = metadata.category.replace('_', ' ').title().replace(' And ', ' & ')
                    tags_display = ', '.join(metadata.tags) if metadata.tags else 'none'
                    print(f"• {metadata.name} ({metadata.id})")
                    print(f"  Category: {category_display}")
                    print(f"  Summary: {metadata.summary}")
                    print(f"  Tags: {tags_display}")
                    print(f"  Version: {metadata.version}")
                    print()
            else:
                print("No packages found matching criteria.")
        else:
            # Show all packages by category
            packages_by_category = InstallerFactory.get_packages_by_category(platform_filter=platform_filter)
            
            if packages_by_category:
                print("📦 Available packages by category:\n")
                
                for category, package_ids in packages_by_category.items():
                    description = InstallerFactory.get_category_description(category)
                    category_display = category.replace('_', ' ').title().replace(' And ', ' & ')
                    
                    print(f"🔧 {category_display}")
                    print(f"   {description}")
                    
                    for package_id in package_ids:
                        try:
                            metadata = InstallerFactory.get_package_metadata(package_id)
                            print(f"   • {metadata.name} ({package_id}) - {metadata.summary}")
                        except Exception:
                            print(f"   • {package_id}")
                    print()
                
                print("💡 Use 'sherpa install <package>' to install")
                print("💡 Use 'sherpa info <package>' for detailed information")
            else:
                print("No packages available for current platform.")
                if platform_filter:
                    print("Use --all-platforms to see packages for other platforms.")
    except Exception as e:
        logger.error(f"Error listing packages: {e}")
        print("Error listing packages. Please check your package structure.")

def handle_install(package_name):
    """Install a specified package by name"""
    available_packages = InstallerFactory.get_available_packages()
    
    if package_name not in available_packages:
        logger.info(f"Package '{package_name}' is not available.")
        logger.info(f"📦 Available packages: {', '.join(available_packages)}")
        return
    
    try:
        # Validate dependencies and conflicts before installation
        # For now, we'll simulate installed packages - in the future this could check actual system state
        installed_packages = []  # TODO: Implement actual installed package detection
        
        validation_issues = InstallerFactory.validate_dependencies_and_conflicts(package_name, installed_packages)
        
        # Check for missing dependencies
        if validation_issues["missing_dependencies"]:
            print(f"⚠️  Missing dependencies for {package_name}:")
            for dep in validation_issues["missing_dependencies"]:
                print(f"   • {dep}")
            print("Please install dependencies first or use automated dependency resolution in the future.")
            return
        
        # Check for conflicts
        if validation_issues["conflicts"]:
            print(f"⚠️  Conflicts detected for {package_name}:")
            for conflict in validation_issues["conflicts"]:
                print(f"   • Conflicts with {conflict}")
            print("Please remove conflicting packages first.")
            return
        
        # Show warnings
        if validation_issues["warnings"]:
            print(f"⚠️  Warnings for {package_name}:")
            for warning in validation_issues["warnings"]:
                print(f"   • {warning}")
            print("Proceeding anyway...")
        
        installer = InstallerFactory.create_installer(package_name)
        
        # 1. Install software (binary/package)
        if not installer.is_software_installed():
            installer.install_software()
        else:
            logger.info(f"{package_name} software already installed")

        # 2. Install configuration files (stow)
        installer.install_config()
        
        # 3. Setup system integration (shell, etc.)
        installer.setup_integration()

        logger.info(f"{package_name} installation completed")
    except ValueError as e:
        logger.error(f"ValueError: {e}")
    except Exception as e:
        logger.error(f"Installation failed: {e}")

def handle_remove(package_name):
    """Remove a specified package by name"""
    available_packages = InstallerFactory.get_available_packages()

    if package_name not in available_packages:
        logger.info(f"Package '{package_name}' is not available.")
        logger.info(f"📦 Available packages: {', '.join(available_packages)}")
        return

    try:
        installer = InstallerFactory.create_installer(package_name)
        
        # 1. Remove system integration (shell, etc.) - FIRST
        installer.uninstall_integration()

        # 2. Remove configuration files (stow)
        installer.uninstall_config()

        # 3. Remove system integration (shell, etc.)
        installer.uninstall_software()

        logger.info(f"{package_name} removal completed")
    except ValueError as e:
        logger.error(f"ValueError: {e}")
    except Exception as e:
        logger.error(f"Removal failed: {e}")

def main():
    """Main entry point for the dotfiles manager."""

    parser = create_parser()
    
    args = parser.parse_args()
    
    # If no command is provided, show help
    if not args.command:
        parser.print_help()
        return 0

    # Dispatcher for commands
    if args.command == "list":
        handle_list(args)
        return 0
    
    elif args.command == "info":
        handle_info(args)
        return 0
    
    elif args.command == "search":
        handle_search(args)
        return 0
    
    elif args.command == "install":
        handle_install(args.package)
        return 0

    elif args.command == "remove":
        handle_remove(args.package)
        return 0


if __name__ == "__main__":
    main()