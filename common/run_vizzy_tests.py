#!/usr/bin/env python
"""
Vizzy Chat Test Runner

Quick script to run all Vizzy Chat tests and generate reports
"""
import os
import sys
import subprocess
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def run_command(cmd, description):
    """Run a shell command and return success status"""
    print_info(f"{description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Failed: {description}")
        print(e.stderr)
        return False, e.stderr

def main():
    print_header("Vizzy Chat Test Suite")
    
    # Check if we're in the correct directory
    if not Path('manage.py').exists():
        print_error("manage.py not found. Please run from python_deckoviz/common directory")
        sys.exit(1)
    
    print_success("Found Django project")
    
    # Test categories
    tests = [
        {
            'name': 'All Vizzy Chat Tests',
            'command': 'python manage.py test apps.vizzy_chat.tests --verbosity=2',
            'required': True
        },
        {
            'name': 'Session Tests Only',
            'command': 'python manage.py test apps.vizzy_chat.tests.test_views_sessions --verbosity=1',
            'required': False
        },
        {
            'name': 'Message Tests Only',
            'command': 'python manage.py test apps.vizzy_chat.tests.test_views_messages --verbosity=1',
            'required': False
        },
        {
            'name': 'Profile Tests Only',
            'command': 'python manage.py test apps.vizzy_chat.tests.test_views_profile --verbosity=1',
            'required': False
        },
        {
            'name': 'Mood & Context Tests Only',
            'command': 'python manage.py test apps.vizzy_chat.tests.test_views_mood_context --verbosity=1',
            'required': False
        }
    ]
    
    results = []
    
    # Run required test (all tests)
    print_header("Running Full Test Suite")
    success, output = run_command(tests[0]['command'], tests[0]['name'])
    results.append({'name': tests[0]['name'], 'success': success})
    
    if not success:
        print_error("❌ FULL TEST SUITE FAILED!")
        print_info("Fix errors above before proceeding")
        sys.exit(1)
    
    print_success("✅ ALL TESTS PASSED!")
    
    # Ask if user wants detailed breakdown
    print_info("\nRun detailed test breakdown? (y/n) [n]: ")
    choice = input().strip().lower()
    
    if choice == 'y':
        print_header("Detailed Test Breakdown")
        for test in tests[1:]:
            success, output = run_command(test['command'], test['name'])
            results.append({'name': test['name'], 'success': success})
    
    # Print summary
    print_header("Test Summary")
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    
    for result in results:
        if result['success']:
            print_success(f"{result['name']}: PASSED")
        else:
            print_error(f"{result['name']}: FAILED")
    
    print(f"\n{Colors.BOLD}Total: {total} | Passed: {passed} | Failed: {failed}{Colors.ENDC}\n")
    
    if failed == 0:
        print_success("🎉 ALL TESTS PASSED! Phase 1.2 is complete and production-ready!")
        
        # Check for coverage
        print_info("\nWould you like to generate a coverage report? (y/n) [n]: ")
        choice = input().strip().lower()
        
        if choice == 'y':
            print_header("Generating Coverage Report")
            run_command(
                'coverage run --source="apps/vizzy_chat" manage.py test apps.vizzy_chat.tests',
                'Running tests with coverage'
            )
            run_command('coverage report', 'Generating coverage report')
            run_command('coverage html', 'Generating HTML coverage report')
            print_success("Coverage report generated in htmlcov/index.html")
        
        return 0
    else:
        print_error("Some tests failed. Please review errors above.")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\n\nTest run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        sys.exit(1)
