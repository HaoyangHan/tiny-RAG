#!/usr/bin/env python3
"""
TinyRAG v1.4 Comprehensive Test Runner.

This script coordinates and runs all modular test suites for comprehensive
API testing following .cursorrules standards for clean code and maintainability.

Test Suites:
- Authentication Tests (auth endpoints)
- Projects Tests (project management) 
- Elements Tests (element CRUD and execution)
- Documents Tests (document upload and processing)
- Users Tests (user management)
- Generations Tests (generation tracking)
- Evaluations Tests (evaluation framework)
- Admin Tests (admin endpoints)
- Legacy Tests (v1.3 backward compatibility)

Usage:
    python run_all_tests.py [--suite SUITE_NAME] [--verbose] [--parallel]
    
Examples:
    python run_all_tests.py                    # Run all tests sequentially
    python run_all_tests.py --suite auth       # Run only auth tests
    python run_all_tests.py --parallel         # Run tests in parallel
    python run_all_tests.py --verbose          # Detailed output
"""

import asyncio
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import aiohttp


class TinyRAGTestRunner:
    """
    Comprehensive test runner for TinyRAG v1.4.
    
    Follows .cursorrules standards for clean code and modular architecture.
    Coordinates execution of all domain-specific test suites.
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize the test runner."""
        self.verbose = verbose
        self.base_url = "http://localhost:8000"
        self.test_suites = {
            "auth": {
                "name": "Authentication Tests",
                "script": "tests/test_auth.py",
                "description": "User registration, login, token management",
                "icon": "🔐"
            },
            "projects": {
                "name": "Projects Tests", 
                "script": "tests/test_projects.py",
                "description": "Project CRUD, collaboration, search",
                "icon": "🏗️"
            },
            "elements": {
                "name": "Elements Tests",
                "script": "tests/test_elements.py", 
                "description": "Element creation, execution, templates",
                "icon": "🧩"
            },
            "documents": {
                "name": "Documents Tests",
                "script": "tests/test_documents.py",
                "description": "Document upload, processing, search",
                "icon": "📄"
            },
            "users": {
                "name": "Users Tests",
                "script": "tests/test_users.py",
                "description": "User profiles, analytics, management",
                "icon": "👤"
            },
            "generations": {
                "name": "Generations Tests",
                "script": "tests/test_generations.py",
                "description": "Generation tracking, metrics, history",
                "icon": "⚡"
            },
            "evaluations": {
                "name": "Evaluations Tests",
                "script": "tests/test_evaluations.py",
                "description": "LLM-as-a-judge, scoring, analytics",
                "icon": "📊"
            },
            "admin": {
                "name": "Admin Tests",
                "script": "tests/test_admin.py",
                "description": "Admin endpoints, system stats, management",
                "icon": "⚙️"
            },
            "legacy": {
                "name": "Legacy Tests",
                "script": "tests/test_legacy.py",
                "description": "v1.3 backward compatibility",
                "icon": "🔄"
            }
        }
        self.results: Dict[str, Dict[str, Any]] = {}
        self.start_time: Optional[float] = None
        
    async def check_server_health(self) -> bool:
        """Check if API server is running and healthy."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        if self.verbose:
                            print(f"✅ Server healthy: {health_data.get('status')}")
                            print(f"   Version: {health_data.get('version')}")
                            print(f"   Models: {len(health_data.get('models', []))}")
                        return True
                    else:
                        print(f"❌ Server unhealthy: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return False
    
    def print_banner(self) -> None:
        """Print test runner banner."""
        print("=" * 70)
        print("🚀 TinyRAG v1.4 Comprehensive Test Suite Runner")
        print("=" * 70)
        print("Rules for AI loaded successfully!")
        print(f"Target Server: {self.base_url}")
        print(f"Test Suites Available: {len(self.test_suites)}")
        print(f"Verbose Mode: {'ON' if self.verbose else 'OFF'}")
        print()
    
    def print_available_suites(self) -> None:
        """Print available test suites."""
        print("📋 AVAILABLE TEST SUITES:")
        print("-" * 50)
        
        for suite_key, suite_info in self.test_suites.items():
            icon = suite_info["icon"]
            name = suite_info["name"]
            desc = suite_info["description"]
            script_path = Path(suite_info["script"])
            exists = "✅" if script_path.exists() else "❌"
            
            print(f"{icon} {exists} {suite_key:<12} - {name}")
            if self.verbose:
                print(f"              {desc}")
                print(f"              Script: {suite_info['script']}")
        print()
    
    async def run_test_suite(self, suite_key: str) -> Dict[str, Any]:
        """
        Run a specific test suite.
        
        Args:
            suite_key: Key of the test suite to run
            
        Returns:
            Test results dictionary
        """
        suite_info = self.test_suites[suite_key]
        script_path = Path(suite_info["script"])
        
        if not script_path.exists():
            return {
                "suite": suite_key,
                "name": suite_info["name"],
                "status": "SKIPPED",
                "reason": "Script not found",
                "duration": 0,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0
            }
        
        print(f"{suite_info['icon']} Running {suite_info['name']}...")
        if self.verbose:
            print(f"   Script: {suite_info['script']}")
            print(f"   Description: {suite_info['description']}")
        
        start_time = time.time()
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=300  # 5 minute timeout per suite
            )
            
            duration = time.time() - start_time
            
            # Parse results from JSON file if available
            result_file = Path(f"{suite_key}_test_results.json")
            tests_run = 0
            tests_passed = 0
            tests_failed = 0
            
            if result_file.exists():
                try:
                    with open(result_file, 'r') as f:
                        test_data = json.load(f)
                        if isinstance(test_data, list):
                            tests_run = len(test_data)
                            tests_passed = sum(1 for t in test_data if t.get("success", False))
                            tests_failed = tests_run - tests_passed
                except Exception as e:
                    if self.verbose:
                        print(f"   Warning: Could not parse results file: {e}")
            
            # Determine status
            if result.returncode == 0:
                status = "PASSED" if tests_failed == 0 else "PARTIAL"
            else:
                status = "FAILED"
            
            suite_result = {
                "suite": suite_key,
                "name": suite_info["name"],
                "status": status,
                "duration": duration,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Print summary
            if status == "PASSED":
                print(f"   ✅ {suite_info['name']} completed successfully")
            elif status == "PARTIAL":
                print(f"   🟡 {suite_info['name']} completed with some failures")
            else:
                print(f"   ❌ {suite_info['name']} failed")
            
            if tests_run > 0:
                print(f"   📊 Tests: {tests_passed}/{tests_run} passed ({(tests_passed/tests_run)*100:.1f}%)")
            
            print(f"   ⏱️  Duration: {duration:.2f}s")
            
            if self.verbose and result.stderr:
                print(f"   ⚠️  Stderr: {result.stderr[:200]}...")
            
            return suite_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"   ⏰ {suite_info['name']} timed out after {duration:.1f}s")
            
            return {
                "suite": suite_key,
                "name": suite_info["name"],
                "status": "TIMEOUT",
                "duration": duration,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0
            }
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"   💥 {suite_info['name']} crashed: {str(e)}")
            
            return {
                "suite": suite_key,
                "name": suite_info["name"],
                "status": "CRASHED",
                "reason": str(e),
                "duration": duration,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0
            }
    
    async def run_suites_sequential(self, suite_keys: List[str]) -> None:
        """Run test suites sequentially."""
        print("🔄 Running test suites sequentially...")
        print()
        
        for suite_key in suite_keys:
            if suite_key not in self.test_suites:
                print(f"❌ Unknown test suite: {suite_key}")
                continue
                
            result = await self.run_test_suite(suite_key)
            self.results[suite_key] = result
            print()
    
    async def run_suites_parallel(self, suite_keys: List[str]) -> None:
        """Run test suites in parallel."""
        print(f"⚡ Running {len(suite_keys)} test suites in parallel...")
        print()
        
        # Filter valid suite keys
        valid_keys = [key for key in suite_keys if key in self.test_suites]
        
        # Run suites concurrently
        tasks = [self.run_test_suite(suite_key) for suite_key in valid_keys]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store results
        for suite_key, result in zip(valid_keys, results):
            if isinstance(result, Exception):
                self.results[suite_key] = {
                    "suite": suite_key,
                    "name": self.test_suites[suite_key]["name"],
                    "status": "CRASHED",
                    "reason": str(result),
                    "duration": 0,
                    "tests_run": 0,
                    "tests_passed": 0,
                    "tests_failed": 0
                }
            else:
                self.results[suite_key] = result
    
    def print_final_summary(self) -> None:
        """Print comprehensive test summary."""
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        print("=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        # Overall statistics
        total_suites = len(self.results)
        passed_suites = sum(1 for r in self.results.values() if r["status"] == "PASSED")
        failed_suites = sum(1 for r in self.results.values() if r["status"] in ["FAILED", "CRASHED", "TIMEOUT"])
        partial_suites = sum(1 for r in self.results.values() if r["status"] == "PARTIAL")
        skipped_suites = sum(1 for r in self.results.values() if r["status"] == "SKIPPED")
        
        total_tests = sum(r["tests_run"] for r in self.results.values())
        total_passed = sum(r["tests_passed"] for r in self.results.values())
        total_failed = sum(r["tests_failed"] for r in self.results.values())
        
        print(f"Test Suites: {total_suites} total")
        print(f"  ✅ Passed: {passed_suites}")
        print(f"  🟡 Partial: {partial_suites}")
        print(f"  ❌ Failed: {failed_suites}")
        print(f"  ⏭️  Skipped: {skipped_suites}")
        print()
        
        if total_tests > 0:
            print(f"Individual Tests: {total_tests} total")
            print(f"  ✅ Passed: {total_passed}")
            print(f"  ❌ Failed: {total_failed}")
            print(f"  📈 Success Rate: {(total_passed/total_tests)*100:.1f}%")
            print()
        
        print(f"Total Duration: {total_duration:.2f}s")
        print()
        
        # Suite-by-suite breakdown
        print("📋 SUITE-BY-SUITE RESULTS:")
        print("-" * 70)
        
        for suite_key, result in self.results.items():
            suite_info = self.test_suites[suite_key]
            icon = suite_info["icon"]
            status_icon = {
                "PASSED": "✅",
                "PARTIAL": "🟡", 
                "FAILED": "❌",
                "CRASHED": "💥",
                "TIMEOUT": "⏰",
                "SKIPPED": "⏭️"
            }.get(result["status"], "❓")
            
            print(f"{icon} {status_icon} {suite_key:<12} - {result['name']}")
            
            if result["tests_run"] > 0:
                success_rate = (result["tests_passed"] / result["tests_run"]) * 100
                print(f"              Tests: {result['tests_passed']}/{result['tests_run']} passed ({success_rate:.1f}%)")
            
            print(f"              Duration: {result['duration']:.2f}s")
            
            if result.get("reason"):
                print(f"              Reason: {result['reason']}")
        
        print()
        
        # Save comprehensive results
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "summary": {
                "total_suites": total_suites,
                "passed_suites": passed_suites,
                "partial_suites": partial_suites,
                "failed_suites": failed_suites,
                "skipped_suites": skipped_suites,
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "success_rate": (total_passed/total_tests)*100 if total_tests > 0 else 0
            },
            "suites": self.results
        }
        
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(summary_data, f, indent=2)
        
        print("💾 Comprehensive results saved to: comprehensive_test_results.json")
        
        # Provide recommendations
        print("\n🎯 RECOMMENDATIONS:")
        if failed_suites == 0 and partial_suites == 0:
            print("  🟢 Excellent! All test suites passed completely.")
            print("  🚀 System is ready for production deployment.")
        elif failed_suites == 0:
            print("  🟡 Good! All suites completed with some test failures.")
            print("  🔧 Review failed tests and address issues.")
        else:
            print("  🟠 Attention needed! Some test suites failed completely.")
            print("  🚨 Critical issues require immediate attention.")
    
    async def run_tests(self, suite_keys: List[str], parallel: bool = False) -> None:
        """
        Run comprehensive tests.
        
        Args:
            suite_keys: List of suite keys to run
            parallel: Whether to run suites in parallel
        """
        self.start_time = time.time()
        
        # Check server health
        print("🔍 Checking server health...")
        server_healthy = await self.check_server_health()
        
        if not server_healthy:
            print("❌ Server is not healthy - aborting tests")
            sys.exit(1)
        
        print("✅ Server is healthy - proceeding with tests")
        print()
        
        # Run tests
        if parallel:
            await self.run_suites_parallel(suite_keys)
        else:
            await self.run_suites_sequential(suite_keys)
        
        # Print final summary
        self.print_final_summary()


async def main():
    """Main function for test runner."""
    parser = argparse.ArgumentParser(
        description="TinyRAG v1.4 Comprehensive Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py                    # Run all tests sequentially
  python run_all_tests.py --suite auth       # Run only auth tests
  python run_all_tests.py --parallel         # Run tests in parallel
  python run_all_tests.py --verbose          # Detailed output
        """
    )
    
    parser.add_argument(
        "--suite",
        choices=["auth", "projects", "elements", "documents", "users", "generations", "evaluations", "admin", "legacy"],
        help="Run specific test suite only"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run test suites in parallel"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available test suites and exit"
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TinyRAGTestRunner(verbose=args.verbose)
    runner.print_banner()
    
    # Handle list command
    if args.list:
        runner.print_available_suites()
        return
    
    # Determine which suites to run
    if args.suite:
        suite_keys = [args.suite]
        print(f"🎯 Running single test suite: {args.suite}")
    else:
        suite_keys = list(runner.test_suites.keys())
        print(f"🎯 Running all {len(suite_keys)} test suites")
    
    runner.print_available_suites()
    
    # Run tests
    await runner.run_tests(suite_keys, parallel=args.parallel)


if __name__ == "__main__":
    asyncio.run(main()) 