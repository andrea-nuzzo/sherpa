import argparse
import sys
import os
from pathlib import Path

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

def handle_list():
    """Return a list of available packages."""

    packages_dir = Path("packages")
    available_packages = []
    
    if not packages_dir.exists():
        print(f"Packages directory '{packages_dir}' does not exist.")
        return available_packages
    
    for package in packages_dir.iterdir():
        if package.is_dir():
            installer_file = package / "installer.py"
            config_dir = package / "config"

            if installer_file.exists() and config_dir.exists():
                available_packages.append(package.name)
                
    return sorted(available_packages)

def handle_install(package_name):
    
def main():
    """Main entry point for the dotfiles manager."""

    parser = create_parser()
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == "list":
        available_packages = handle_list()
        
        if available_packages:
            print("Available packages:")
            for package in available_packages:
                print(f" - {package}")
        else:
            print("📦 No packages available.")
        return 0
    
    
    

if __name__ == "__main__":
    main()