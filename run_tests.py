#!/usr/bin/env python3
"""
Test runner script for the High School Management System API.

This script provides convenient commands to run different types of tests.
"""
import subprocess
import sys
import argparse


def run_command(command, description):
    """Run a command and handle the output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ {description} completed successfully")
        return True


def main():
    parser = argparse.ArgumentParser(description="Test runner for High School Management System API")
    parser.add_argument(
        "test_type", 
        choices=["all", "unit", "integration", "performance", "coverage", "quick"],
        nargs="?",
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests with verbose output"
    )
    
    args = parser.parse_args()
    
    base_command = "python -m pytest"
    if args.verbose:
        base_command += " -v"
    
    commands = []
    
    if args.test_type == "all":
        commands = [
            (f"{base_command} tests/ --cov=src --cov-report=term-missing", "All tests with coverage")
        ]
    elif args.test_type == "unit":
        commands = [
            (f"{base_command} tests/test_app.py", "Unit tests only")
        ]
    elif args.test_type == "integration":
        commands = [
            (f"{base_command} tests/test_integration.py", "Integration tests only")
        ]
    elif args.test_type == "performance":
        commands = [
            (f"{base_command} tests/test_performance.py -s", "Performance tests only")
        ]
    elif args.test_type == "coverage":
        commands = [
            (f"{base_command} tests/ --cov=src --cov-report=html --cov-report=term-missing", "All tests with HTML coverage report")
        ]
    elif args.test_type == "quick":
        commands = [
            (f"{base_command} tests/test_app.py -x", "Quick unit tests (fail fast)")
        ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
            break
    
    if success:
        print(f"\n🎉 All tests completed successfully!")
        if args.test_type == "coverage":
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()