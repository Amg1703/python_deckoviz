#!/usr/bin/env python3
"""
Setup script for creating a virtual environment for Deckoviz Personal Painter.
This script creates a virtual environment and installs the required dependencies.
"""

import os
import subprocess
import sys
import venv
from pathlib import Path

# Configuration
VENV_DIR = "venv"
REQUIREMENTS_PATH = os.path.join("deckoviz_ai", "streamlit", "requirements.txt")

def create_venv():
    """Create a virtual environment if it doesn't exist."""
    print(f"Creating virtual environment in {VENV_DIR}...")
    venv_path = Path(VENV_DIR)
    
    if venv_path.exists():
        print(f"Virtual environment already exists at {VENV_DIR}")
        return True
    
    try:
        venv.create(VENV_DIR, with_pip=True)
        print(f"Created virtual environment at {VENV_DIR}")
        return True
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return False

def get_pip_path():
    """Get the path to pip in the virtual environment."""
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "pip")
    else:
        return os.path.join(VENV_DIR, "bin", "pip")

def install_dependencies():
    """Install dependencies in the virtual environment."""
    pip_path = get_pip_path()
    
    if not os.path.exists(pip_path):
        print(f"Error: Could not find pip at {pip_path}")
        return False
    
    print("Installing dependencies...")
    try:
        # Upgrade pip first
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", REQUIREMENTS_PATH], check=True)
        
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def main():
    """Main function to set up the virtual environment."""
    if not create_venv():
        return 1
    
    if not install_dependencies():
        return 1
    
    print("\nSetup complete! You can now run the personal painter app with:")
    if sys.platform == "win32":
        print(f".\\{VENV_DIR}\\Scripts\\python run_personal_painter.py")
    else:
        print(f"./{VENV_DIR}/bin/python run_personal_painter.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
