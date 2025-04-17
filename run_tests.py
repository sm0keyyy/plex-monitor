#!/usr/bin/env python3
"""
Test runner for Plex Monitor.
This script discovers and runs all tests in the tests directory.
"""

import unittest
import os
import sys

def run_tests():
    """Discover and run all tests in the tests directory."""
    # Add the parent directory to the path so tests can import the main module
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Discover all tests in the tests directory
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return non-zero exit code if tests failed
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
