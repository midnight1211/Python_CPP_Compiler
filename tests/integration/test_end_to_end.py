"""
End-to-end integration tests.
Tests the complete compilation pipeline from source to assembly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.compiler import Compiler, CompilerError


class TestResult:
    """Represents a test result."""

    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message


def run_test(test_name: str, source: str, should_succeed: bool = True) -> TestResult:
    """Run a single integration test."""
    try:
        compiler = Compiler(optimization_level=2, debug=False)
        assembly = compiler.compile(source, f"<test:{test_name}>")

        if should_succeed:
            # Check that assembly was generated
            if assembly and len(assembly) > 0:
                return TestResult(test_name, True, "Compilation successful")
            else:
                return TestResult(test_name, False, "No assembly generated")
        else:
            return TestResult(test_name, False, "Should have failed but succeeded")

    except CompilerError as e:
        if not should_succeed:
            return TestResult(test_name, True, f"Correctly caught error: {str(e)[:50]}...")
        else:
            return TestResult(test_name, False, f"Unexpected error: {e}")
    except Exception as e:
        return TestResult(test_name, False, f"Unexpected exception: {e}")


def test_simple_function():
    """Test simple function compilation."""
    source = """
    int add(int a, int b) {
        return a + b;
    }
    """
    return run_test("Simple Function", source, should_succeed=True)


def test_main_function():
    """Test main function."""
    source = """
    int main() {
        int x = 42;
        return x;
    }
    """
    return run_test("Main Function", source, should_succeed=True)


def test_control_flow():
    """Test if-else statements."""
    source = """
    int max(int a, int b) {
        if (a > b) {
            return a;
        } else {
            return b;
        }
    }
    """
    return run_test("Control Flow", source, should_succeed=True)


def test_while_loop():
    """Test while loops."""
    source = """
    int sum(int n) {
        int result = 0;
        int i = 1;
        while (i <= n) {
            result = result + i;
            i = i + 1;
        }
        return result;
    }
    """
    return run_test("While Loop", source, should_succeed=True)


def test_for_loop():
    """Test for loops."""
    source = """
    int factorial(int n) {
        int result = 1;
        for (int i = 1; i <= n; i++) {
            result = result * i;
        }
        return result;
    }
    """
    return run_test("For Loop", source, should_succeed=True)


def test_function_calls():
    """Test function calls."""
    source = """
    int double_value(int x) {
        return x * 2;
    }

    int main() {
        int a = 5;
        int b = double_value(a);
        return b;
    }
    """
    return run_test("Function Calls", source, should_succeed=True)


def test_recursion():
    """Test recursive functions."""
    source = """
    int fibonacci(int n) {
        if (n <= 1) {
            return n;
        }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    """
    return run_test("Recursion", source, should_succeed=True)


def test_class_basic():
    """Test basic class definition."""
    source = """
    class Point {
    public:
        int x;
        int y;

        Point(int x_val, int y_val) : x(x_val), y(y_val) {}

        int getX() const {
            return x;
        }
    };
    """
    return run_test("Basic Class", source, should_succeed=True)


def test_namespace():
    """Test namespace."""
    source = """
    namespace Math {
        int add(int a, int b) {
            return a + b;
        }
    }
    """
    return run_test("Namespace", source, should_succeed=True)


def test_template():
    """Test template function."""
    source = """
    template<typename T>
    T maximum(T a, T b) {
        return (a > b) ? a : b;
    }
    """
    return run_test("Template", source, should_succeed=True)


def test_undeclared_variable():
    """Test undeclared variable error."""
    source = """
    int main() {
        int x = y;  // y is undeclared
        return x;
    }
    """
    return run_test("Undeclared Variable", source, should_succeed=False)


def test_syntax_error():
    """Test syntax error detection."""
    source = """
    int main() {
        int x = 5
        return x;
    }
    """
    return run_test("Syntax Error", source, should_succeed=False)


def test_type_error():
    """Test type error detection."""
    source = """
    int main() {
        int x = 5;
        int* ptr = x;  // Type error
        return 0;
    }
    """
    return run_test("Type Error", source, should_succeed=False)


def test_optimization_levels():
    """Test different optimization levels."""
    source = """
    int compute() {
        int a = 2 + 3;
        int b = a * 1;
        int c = b + 0;
        return c;
    }
    """

    results = []
    for opt_level in [0, 1, 2, 3]:
        try:
            compiler = Compiler(optimization_level=opt_level, debug=False)
            assembly = compiler.compile(source, f"<test:opt-{opt_level}>")
            results.append(TestResult(
                f"Optimization -O{opt_level}",
                True,
                f"Generated {compiler.stats['assembly_lines']} lines"
            ))
        except Exception as e:
            results.append(TestResult(f"Optimization -O{opt_level}", False, str(e)))

    return results


def main():
    """Run all integration tests."""
    print("=" * 80)
    print("END-TO-END INTEGRATION TESTS")
    print("=" * 80)
    print()

    # Define test suite
    tests = [
        test_simple_function,
        test_main_function,
        test_control_flow,
        test_while_loop,
        test_for_loop,
        test_function_calls,
        test_recursion,
        test_class_basic,
        test_namespace,
        test_template,
        test_undeclared_variable,
        test_syntax_error,
        test_type_error,
    ]

    results = []

    # Run tests
    print("Running tests...")
    print("-" * 80)

    for test_func in tests:
        result = test_func()
        if isinstance(result, list):
            results.extend(result)
        else:
            results.append(result)

        # Print result
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"{status:8} {result.name:30} {result.message}")

    # Run optimization tests
    print("\nTesting optimization levels...")
    opt_results = test_optimization_levels()
    for result in opt_results:
        results.append(result)
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"{status:8} {result.name:30} {result.message}")

    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    total = len(results)

    print(f"Total tests:  {total}")
    print(f"Passed:       {passed}")
    print(f"Failed:       {failed}")
    print(f"Success rate: {passed / total * 100:.1f}%")

    if failed == 0:
        print()
        print("✓ All tests passed!")
        return 0
    else:
        print()
        print("✗ Some tests failed.")
        print("\nFailed tests:")
        for result in results:
            if not result.passed:
                print(f"  - {result.name}: {result.message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())