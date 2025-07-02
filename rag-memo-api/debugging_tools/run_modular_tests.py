#!/usr/bin/env python3
"""
TinyRAG v1.4 Modular Test Runner.

This script runs focused test suites organized by domain/subroute
following .cursorrules standards for clean, maintainable code.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

async def run_test_suite(suite_name: str, script_path: str) -> bool:
    """Run a specific test suite."""
    print(f"\n{'='*60}")
    print(f"🧪 Running {suite_name}")
    print(f"{'='*60}")
    
    if not Path(script_path).exists():
        print(f"❌ Test script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=Path.cwd(),
            timeout=180  # 3 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {suite_name} completed successfully")
            return True
        else:
            print(f"❌ {suite_name} failed with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {suite_name} timed out")
        return False
    except Exception as e:
        print(f"💥 {suite_name} crashed: {e}")
        return False

async def main():
    """Run all available test suites."""
    print("Rules for AI loaded successfully!")
    print("🚀 TinyRAG v1.4 Modular Test Runner")
    
    test_suites = [
        ("Authentication Tests", "tests/test_auth.py"),
        ("Projects Tests", "tests/test_projects.py"),
        # Add more as we create them
    ]
    
    results = []
    for suite_name, script_path in test_suites:
        success = await run_test_suite(suite_name, script_path)
        results.append((suite_name, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for suite_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {suite_name}")
    
    print(f"\nOverall: {passed}/{total} test suites passed ({(passed/total)*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main())
