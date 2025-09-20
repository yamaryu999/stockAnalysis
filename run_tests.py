#!/usr/bin/env python3
"""
Test Runner for Stock Analysis Tool
"""

import unittest
import sys
import os
import argparse
import time
from io import StringIO

def run_tests(test_pattern=None, verbose=False, coverage=False):
    """Run tests with specified options"""
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Discover tests
    if test_pattern:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_pattern)
    else:
        loader = unittest.TestLoader()
        start_dir = os.path.join(os.path.dirname(__file__), 'tests')
        suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    if verbose:
        verbosity = 2
    else:
        verbosity = 1
    
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    
    print("=" * 70)
    print("🚀 Stock Analysis Tool - Test Suite")
    print("=" * 70)
    print(f"📅 Test Run: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 Test Pattern: {test_pattern or 'All Tests'}")
    print(f"📊 Verbosity: {'High' if verbose else 'Normal'}")
    print("=" * 70)
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📋 Test Summary")
    print("=" * 70)
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"🚫 Errors: {len(result.errors)}")
    print(f"⏱️  Duration: {end_time - start_time:.2f} seconds")
    
    if result.failures:
        print("\n❌ Test Failures:")
        for test, tb in result.failures:
            try:
                msg = tb.split('AssertionError: ')[-1].split('\n')[0]
            except Exception:
                msg = tb.split('\n')[-1].strip() if tb else 'AssertionError'
            print(f"  - {test}: {msg}")
    
    if result.errors:
        print("\n🚫 Test Errors:")
        for test, tb in result.errors:
            try:
                msg = tb.split('\n')[-2].strip()
            except Exception:
                msg = tb.split('\n')[-1].strip() if tb else 'Error'
            print(f"  - {test}: {msg}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All tests passed!")
    elif success_rate >= 90:
        print("✅ Most tests passed!")
    elif success_rate >= 70:
        print("⚠️  Some tests failed")
    else:
        print("❌ Many tests failed")
    
    print("=" * 70)
    
    return result.wasSuccessful()

def run_specific_test_suite(suite_name):
    """Run specific test suite"""
    test_modules = {
        'performance': 'tests.test_performance_optimizer',
        'database': 'tests.test_database_manager',
        'ai': 'tests.test_enhanced_ai_analyzer',
        'realtime': 'tests.test_realtime_manager',
        'integration': 'tests.test_integration',
        'e2e': 'tests.test_e2e'
    }
    
    if suite_name in test_modules:
        return run_tests(test_modules[suite_name], verbose=True)
    else:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(test_modules.keys())}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run tests for Stock Analysis Tool')
    parser.add_argument('--suite', '-s', choices=['performance', 'database', 'ai', 'realtime', 'integration', 'e2e'],
                       help='Run specific test suite')
    parser.add_argument('--pattern', '-p', help='Run tests matching pattern')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Run with coverage (requires coverage.py)')
    parser.add_argument('--quick', '-q', action='store_true', help='Run quick tests only')
    
    args = parser.parse_args()
    
    if args.suite:
        success = run_specific_test_suite(args.suite)
    else:
        success = run_tests(args.pattern, args.verbose, args.coverage)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
