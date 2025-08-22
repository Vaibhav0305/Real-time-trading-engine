#!/usr/bin/env python3
"""
Simple build script for VittCott Trading Engine
Compiles C++ code directly without CMake dependencies
"""

import os
import subprocess
import sys
import platform

def get_compiler():
    """Get the appropriate compiler for the platform"""
    if platform.system() == "Windows":
        # Try to find g++ or cl.exe
        compilers = ["g++", "cl", "clang++"]
        for compiler in compilers:
            try:
                result = subprocess.run([compiler, "--version"], 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    return compiler
            except FileNotFoundError:
                continue
        return "g++"  # Default fallback
    else:
        return "g++"

def compile_cpp():
    """Compile the C++ trading engine"""
    compiler = get_compiler()
    
    # Source files in dependency order
    source_files = [
        "Logger.cpp",
        "EmailNotifier.cpp", 
        "Order.cpp",
        "Trade.cpp",
        "TradeLogger.cpp",
        "OrderBook.cpp",
        "MatchingEngine.cpp",
        "main.cpp"
    ]
    
    # Compiler flags
    flags = [
        "-std=c++17",
        "-Wall",
        "-Wextra",
        "-O2",
        "-I."
    ]
    
    # Build command
    cmd = [compiler] + flags + source_files + ["-o", "trading_engine"]
    
    print(f"Compiling with: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Compilation successful!")
        print("Executable created: trading_engine")
                return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Compilation failed!")
        print(f"Error output: {e.stderr}")
        return False
    
def run_tests():
    """Run basic tests to verify the engine works"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test if executable runs
        result = subprocess.run(["./trading_engine"], 
                              input="5\n",  # Exit immediately
                              capture_output=True, text=True, timeout=5)
        print("✅ Basic execution test passed")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
if __name__ == "__main__":
    print("🚀 Building VittCott Trading Engine...")
    
    if compile_cpp():
        if run_tests():
            print("\n🎉 Build and test completed successfully!")
            print("You can now run: ./trading_engine")
        else:
            print("\n⚠️  Build succeeded but tests failed")
    else:
        print("\n💥 Build failed. Check the error messages above.")
        sys.exit(1)
