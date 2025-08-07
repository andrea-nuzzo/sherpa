import os
import sys
import argparse
import logging
from pathlib import Path


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_parser():
    """Create and return the argument parser for the dotfiles manager."""
    parser = argparse.ArgumentParser(
        prog="dotfiles",
        description="🚀 Dotfiles Manage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            %(prog)s remove <name package>    # Remove specified package
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
    
    install_parser = subparsers.add_parser(
        "install",
        help="%(prog)s install <name package> - Install specified package"
    )
    
    install_parser.add_argument(
        "package",
        help="Package name to install (e.g., starship)"
    )
        
    return parser

def get_available_packages():
    """Return a list of available packages."""

    packages_dir = Path("packages")
    available_packages = []
    
    if not packages_dir.exists():
        return available_packages
    
    for package in packages_dir.iterdir():
        if package.is_dir():
            installer_file = package / "installer.py"
            config_dir = package / "config"

            if installer_file.exists() and config_dir.exists():
                available_packages.append(package.name)
                
    return sorted(available_packages)

def handle_list():
    """Handle the list command - show available packages."""
    available_packages = get_available_packages()
    
    if available_packages:
        logger.info("📦 Available packages:")
        for package in available_packages:
            logger.info(f"  • {package}")
        logger.info(f"\n💡 Use 'dotfiles install <package>' to install")
    else:
        logger.info("No packages available.")
        logger.info("Create packages in: packages/<name>/installer.py + packages/<name>/config/")

def handle_install(package_name):
    """Install a specified package by name"""
    packages  = get_available_packages()
    
    if package_name not in packages:
        logger.info(f"Package '{package_name}' is not available.")
        logger.info(f"📦 Available packages: {', '.join(packages)}")
        return
    
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
        handle_list()
        return 0
    
    elif args.command == "install":
        handle_install(args.package)
        return 0
    
    
if __name__ == "__main__":
    main()