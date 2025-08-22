#!/usr/bin/env python3
"""
Build and Run Script for VittCott Trading Platform
This script automates the build process for the C++ engine and runs the backend server.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            raise
        return e

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required")
        return False
    
    # Check if cmake is available
    try:
        run_command("cmake --version", check=False)
        print("✓ CMake found")
    except:
        print("✗ CMake not found. Please install CMake")
        return False
    
    # Check if ninja is available
    try:
        run_command("ninja --version", check=False)
        print("✓ Ninja found")
    except:
        print("✗ Ninja not found. Please install Ninja")
        return False
    
    return True

def build_cpp_engine():
    """Build the C++ trading engine with pybind11"""
    print("\nBuilding C++ trading engine...")
    
    # Create build directory
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)
    
    # Configure with CMake
    print("Configuring with CMake...")
    cmake_command = "cmake -G Ninja -DCMAKE_BUILD_TYPE=Release .."
    result = run_command(cmake_command, cwd=build_dir)
    
    if result.returncode != 0:
        print("CMake configuration failed")
        return False
    
    # Build with Ninja
    print("Building with Ninja...")
    build_command = "ninja"
    result = run_command(build_command, cwd=build_dir)
    
    if result.returncode != 0:
        print("Build failed")
        return False
    
    # Copy the built module to the project root for Python import
    module_name = "trading_engine"
    if platform.system() == "Windows":
        module_name += ".pyd"
    else:
        module_name += ".so"
    
    source_path = build_dir / module_name
    target_path = Path(module_name)
    
    if source_path.exists():
        shutil.copy2(source_path, target_path)
        print(f"✓ C++ engine built successfully: {target_path}")
        return True
    else:
        print(f"✗ Built module not found at {source_path}")
        return False

def install_python_dependencies():
    """Install Python dependencies for the backend"""
    print("\nInstalling Python dependencies...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("Backend directory not found")
        return False
    
    requirements_file = backend_dir / "requirements.txt"
    if not requirements_file.exists():
        print("requirements.txt not found")
        return False
    
    # Install dependencies
    install_command = f"{sys.executable} -m pip install -r {requirements_file}"
    result = run_command(install_command)
    
    if result.returncode == 0:
        print("✓ Python dependencies installed successfully")
        return True
    else:
        print("✗ Failed to install Python dependencies")
        return False

def run_backend():
    """Run the FastAPI backend server"""
    print("\nStarting FastAPI backend server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("Backend directory not found")
        return False
    
    # Change to backend directory and run the server
    os.chdir(backend_dir)
    
    # Run with uvicorn
    run_command = f"{sys.executable} -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    
    print("Starting server... Press Ctrl+C to stop")
    try:
        subprocess.run(run_command, shell=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error running server: {e}")
        return False
    
    return True

def main():
    """Main build and run process"""
    print("VittCott Trading Platform - Build and Run Script")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("Dependency check failed. Please install missing dependencies.")
        return 1
    
    # Build C++ engine
    if not build_cpp_engine():
        print("C++ engine build failed.")
        return 1
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("Python dependency installation failed.")
        return 1
    
    # Run backend
    if not run_backend():
        print("Backend server failed to start.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
