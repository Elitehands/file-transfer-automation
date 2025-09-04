"""Build and test script for File Transfer Automation"""

import subprocess
import sys
import shutil
import os
from pathlib import Path
import argparse

# Project paths
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"

def clean():
    """Clean build directories"""
    print("Cleaning build directories...")
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
    
    # Remove spec files
    for spec_file in PROJECT_ROOT.glob("*.spec"):
        spec_file.unlink()
    
    print("Clean complete.")

def run_tests():
    """Run all tests using unittest discover"""
    print("Running tests...")
    
    # Make sure src directory is in path
    src_path = PROJECT_ROOT / "src"
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Run tests
    try:
        import unittest
        tests = unittest.defaultTestLoader.discover(".", pattern="test_*.py")
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(tests)
        
        print(f"\nTests run: {result.testsRun}")
        print(f"Errors: {len(result.errors)}")
        print(f"Failures: {len(result.failures)}")
        
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def build_demo():
    """Build demo application"""
    print("Building demo application...")
    try:
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--name=FileTransferDemo",
            "demo_app.py"
        ], check=True)
        print("Build successful!")
        return True
    except Exception as e:
        print(f"Build failed: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Build and test File Transfer Automation")
    parser.add_argument("--test", action="store_true", help="Run tests only")
    parser.add_argument("--build", action="store_true", help="Build only (skip tests)")
    parser.add_argument("--clean", action="store_true", help="Clean only")
    args = parser.parse_args()
    
    # Print header
    print("=" * 70)
    print(f" FILE TRANSFER AUTOMATION - BUILD TOOL")
    print("=" * 70)
    print(f"Date: 2025-09-04 08:10:25")
    print(f"User: {os.environ.get('USERNAME', 'TobiWilliams001')}")
    print("=" * 70)
    
    # Clean is always performed unless only testing
    if not args.test or args.clean:
        clean()
        
    if args.clean:
        return 0
        
    # Run tests unless build-only specified
    tests_passed = True
    if not args.build:
        tests_passed = run_tests()
        if not tests_passed and not args.test:
            print("Tests failed! Build aborted.")
            return 1
    
    # Build unless test-only specified
    if not args.test and (tests_passed or args.build):
        if build_demo():
            print(f"Demo built successfully: {DIST_DIR}/FileTransferDemo.exe")
        else:
            print("Build failed!")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())