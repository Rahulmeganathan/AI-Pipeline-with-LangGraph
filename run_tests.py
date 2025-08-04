#!/usr/bin/env python3
"""
Test runner for the AI Pipeline project.
Runs all unit tests and provides a summary report.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run all tests and provide a summary."""
    print("🧪 Running AI Pipeline Tests")
    print("=" * 50)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Change to project root
    os.chdir(project_root)
    
    # Run tests with pytest
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], capture_output=True, text=True)
        
        print("Test Results:")
        print("-" * 30)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        # Print test output
        if result.stdout:
            print("\nTest Output:")
            print(result.stdout)
        
        if result.stderr:
            print("\nTest Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        return False


def run_individual_test_files():
    """Run individual test files for detailed testing."""
    print("\n🔍 Running Individual Test Files")
    print("=" * 40)
    
    test_files = [
        "tests/test_weather_service.py",
        "tests/test_rag_service.py", 
        "tests/test_agent_graph.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nRunning {test_file}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    test_file, 
                    "-v"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ {test_file} - PASSED")
                else:
                    print(f"❌ {test_file} - FAILED")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ Error running {test_file}: {str(e)}")
                all_passed = False
        else:
            print(f"⚠️  {test_file} not found")
    
    return all_passed


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking Dependencies")
    print("=" * 30)
    
    required_packages = [
        "langchain",
        "langchain-openai", 
        "langchain-community",
        "langgraph",
        "langsmith",
        "qdrant-client",
        "streamlit",
        "pytest"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies are installed!")
        return True


def main():
    """Main test runner function."""
    print("🚀 AI Pipeline Test Suite")
    print("=" * 40)
    
    # Check dependencies first
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Please install missing dependencies before running tests.")
        return 1
    
    # Run individual test files
    individual_tests_ok = run_individual_test_files()
    
    # Run all tests together
    print("\n" + "=" * 50)
    all_tests_ok = run_tests()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    
    if individual_tests_ok and all_tests_ok:
        print("🎉 All tests passed successfully!")
        print("✅ Dependencies: OK")
        print("✅ Individual tests: OK") 
        print("✅ Full test suite: OK")
        return 0
    else:
        print("❌ Some tests failed!")
        if not individual_tests_ok:
            print("❌ Individual tests: FAILED")
        if not all_tests_ok:
            print("❌ Full test suite: FAILED")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 