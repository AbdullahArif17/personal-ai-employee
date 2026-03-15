#!/usr/bin/env python3
"""
Test runner for Gold tier features of the Personal AI Employee system.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all Gold tier feature tests."""
    print("Running Gold tier feature tests...")

    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Define test files to run
    test_files = [
        "tests/test_gold_tier_features.py",
        "tests/end_to_end_tests.py"
    ]

    all_passed = True

    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n--- Running {test_file} ---")
            result = subprocess.run([sys.executable, "-m", "pytest", test_file, "-v"])

            if result.returncode != 0:
                print(f"❌ Tests in {test_file} failed!")
                all_passed = False
            else:
                print(f"✅ Tests in {test_file} passed!")
        else:
            print(f"⚠️  Test file {test_file} not found, skipping...")

    if all_passed:
        print("\n🎉 All Gold tier tests passed!")
        return 0
    else:
        print("\n💥 Some Gold tier tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())