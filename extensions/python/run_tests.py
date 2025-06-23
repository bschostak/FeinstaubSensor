#!/usr/bin/env python3
"""
Test runner for the FeinstaubSensor project.
"""

import unittest
import sys
import os

# Add the Python extension directory to the path
python_ext_dir = os.path.join(os.path.dirname(__file__), 'extensions', 'python')
sys.path.insert(0, python_ext_dir)

def run_all_tests():
    """Discover and run all tests in the tests directory."""
    # Discover tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(python_ext_dir, 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
