"""
Example usage and testing of the IR generator and optimizer.
Demonstrates IR generation and optimization passes.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.ir import IRGenerator, optimize_ir


def compile_to_ir(source: str, optimize: bool = False, opt_level: int = 2) -> None:
    """Helper to compile source to IR."""
    try:
        # Lex
        print("Lexing...")
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        print(f"✓ Generated {len(tokens)} tokens")

        # Parse
        print("\nParsing...")
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"✓ Generated AST with {len(ast.declarations)} declarations")

        # Semantic analysis
        print("\nSemantic analysis...")
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)
        if not success:
            print("✗ Semantic errors found:")
            analyzer.print_errors()
            return
        print("✓ Semantic analysis passed")

        # Generate IR
        print("\nGenerating IR...")
        ir_gen = IRGenerator()
        ir_program = ir_gen.generate(ast)
        print(f"✓ Generated {len(ir_program.functions)} functions")

        print("\n" + "=" * 80)
        print("UNOPTIMIZED IR")
        print("=" * 80)
        print(ir_program)

        # Optimize
        if optimize:
            print("\n" + "=" * 80)
            print(f"OPTIMIZING (level {opt_level})...")
            print("=" * 80)
            optimized = optimize_ir(ir_program, level=opt_level)

            print("\n" + "=" * 80)
            print("OPTIMIZED IR")
            print("=" * 80)
            print(optimized)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def example_basic():
    """Basic IR generation."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Function")
    print("=" * 80)

    source = """
    int add(int a, int b) {
        return a + b;
    }
    """

    print("\nSource Code:")
    print(source)
    compile_to_ir(source)


def example_arithmetic():
    """Arithmetic operations."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Arithmetic Operations")
    print("=" * 80)

    source = """
    int calculate() {
        int a = 10;
        int b = 20;
        int sum = a + b;
        int diff = a - b;
        int prod = a * b;
        int quot = a / b;
        return sum;
    }
    """

    print("\nSource Code:")
    print(source)
    compile_to_ir(source, optimize=True)


def example_control_flow():
    """Control flow statements."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Control Flow")
    print("=" * 80)

    source = """
    int max(int a, int b) {
        if (a > b) {
            return a;
        } else {
            return b;
        }
    }
    """

    print("\nSource Code:")
    print(source)
    compile_to_ir(source)


def example_loops():
    """Loop structures."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Loops")
    print("=" * 80)

    source = """
    int sum_to_n(int n) {
        int sum = 0;
        for (int i = 1; i <= n; i++) {
            sum = sum + i;
        }
        return sum;
    }
    """

    print("\nSource Code:")
    print(source)
    compile_to_ir(source)


def example_while_loop():
    """While loop."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: While Loop")
    print("=" * 80)

    source = """
    int factorial(int n) {
        int result = 1;
        while (n > 1) {
            result = result * n;
            n = n - 1;
        }
        return result;
    }
    """

    print("\nSource Code:")
    print(source)
    compile_to_ir(source)


def example_constant_folding():
    """Demonstrate constant folding optimization."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Constant Folding")
    print("=" * 80)

    source = """
    int compute() {
        int x = 2 + 3;
        int y = x * 4;
        int z = y + 10;
        return z;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nThis demonstrates constant folding optimization.")
    compile_to_ir(source, optimize=True, opt_level=3)


def example_function_call():
    """Function calls."""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Function Calls")
    print("=" * 80)

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

    print("\nSource Code:")
    print(source)
    compile_to_ir(source)


def example_complex():
    """Complex program."""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Complex Program")
    print("=" * 80)

    source = """
    int fibonacci(int n) {
        if (n <= 1) {
            return n;
        }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }

    int main() {
        int result = fibonacci(10);
        return result;
    }
    """

    print("\nSource Code:")
    print(source)
    compile_to_ir(source, optimize=True)


def example_ternary():
    """Ternary operator."""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Ternary Operator")
    print("=" * 80)

    source = """
    int abs(int x) {
        int result = (x < 0) ? -x : x;
        return result;
    }
    """

    print("\nSource Code:")
    print(source)
    compile_to_ir(source)


def example_increment():
    """Increment/decrement operators."""
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Increment/Decrement")
    print("=" * 80)

    source = """
    int test() {
        int x = 0;
        x++;
        x--;
        ++x;
        --x;
        return x;
    }
    """

    print("\nSource Code:")
    print(source)
    compile_to_ir(source)


def example_optimization_comparison():
    """Compare optimized vs unoptimized."""
    print("\n" + "=" * 80)
    print("EXAMPLE 11: Optimization Comparison")
    print("=" * 80)

    source = """
    int calculate() {
        int a = 5;
        int b = a;
        int c = b;
        int d = 2 + 3;
        int e = d * 1;
        int f = e + 0;
        return f;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nThis shows multiple optimizations:")
    print("- Constant folding (2 + 3)")
    print("- Arithmetic simplification (x * 1, x + 0)")
    print("- Copy propagation (a = b; c = a)")
    print("- Dead code elimination")
    compile_to_ir(source, optimize=True, opt_level=3)


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("IR GENERATOR AND OPTIMIZER EXAMPLES")
    print("=" * 80)

    examples = [
        ("1", "Basic Function", example_basic),
        ("2", "Arithmetic Operations", example_arithmetic),
        ("3", "Control Flow", example_control_flow),
        ("4", "Loops", example_loops),
        ("5", "While Loop", example_while_loop),
        ("6", "Constant Folding", example_constant_folding),
        ("7", "Function Calls", example_function_call),
        ("8", "Complex Program", example_complex),
        ("9", "Ternary Operator", example_ternary),
        ("10", "Increment/Decrement", example_increment),
        ("11", "Optimization Comparison", example_optimization_comparison),
    ]

    if len(sys.argv) > 1:
        choice = sys.argv[1]
        for num, name, func in examples:
            if choice == num:
                func()
                return
        print(f"Unknown example: {choice}")
    else:
        print("\nAvailable examples:")
        for num, name, _ in examples:
            print(f"  {num}. {name}")
        print("\nUsage: python test_ir.py [example_number]")
        print("   or: python test_ir.py all\n")

        choice = input("Choose an example (or 'all' to run all): ").strip()

        if choice == 'all':
            for num, name, func in examples:
                func()
        else:
            for num, name, func in examples:
                if choice == num:
                    func()
                    return
            print(f"Unknown example: {choice}")


if __name__ == "__main__":
    main()