"""
Example usage and testing of the semantic analyzer.
Demonstrates semantic analysis, symbol tables, and type checking.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer import Lexer, LexerError
from src.parser import Parser, ParserError
from src.semantic import SemanticAnalyzer, SemanticError


def analyze_code(source: str, show_symbol_table: bool = False) -> bool:
    """Helper function to analyze C++ code."""
    try:
        # Lex
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        # Parse
        parser = Parser(tokens)
        ast = parser.parse()

        # Semantic analysis
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)

        if success:
            print("✓ Semantic analysis passed")
            if show_symbol_table:
                analyzer.dump_symbol_table()
        else:
            analyzer.print_errors()

        return success

    except (LexerError, ParserError) as e:
        print(f"Error: {e}")
        return False


def example_basic():
    """Basic semantic analysis."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Semantic Analysis")
    print("=" * 80)

    source = """
    int add(int a, int b) {
        return a + b;
    }

    int main() {
        int x = 5;
        int y = 10;
        int result = add(x, y);
        return result;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis:")
    analyze_code(source, show_symbol_table=True)


def example_undeclared_variable():
    """Test undeclared variable error."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Undeclared Variable Error")
    print("=" * 80)

    source = """
    int main() {
        int x = 5;
        int y = z;  // z is not declared
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis (should fail):")
    analyze_code(source)


def example_type_mismatch():
    """Test type mismatch error."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Type Mismatch Error")
    print("=" * 80)

    source = """
    int main() {
        int x = 5;
        int* ptr = x;  // Cannot assign int to int*
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis (should fail):")
    analyze_code(source)


def example_redefinition():
    """Test redefinition error."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Redefinition Error")
    print("=" * 80)

    source = """
    int main() {
        int x = 5;
        int x = 10;  // x already declared
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis (should fail):")
    analyze_code(source)


def example_scope():
    """Test scope resolution."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Scope Resolution")
    print("=" * 80)

    source = """
    int x = 100;  // Global x

    int main() {
        int x = 5;  // Local x (shadows global)

        {
            int x = 10;  // Block-local x
            int y = x;   // Uses block-local x
        }

        int z = x;  // Uses function-local x
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis:")
    analyze_code(source, show_symbol_table=True)


def example_class():
    """Test class analysis."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Class Analysis")
    print("=" * 80)

    source = """
    class Rectangle {
    public:
        int width;
        int height;

        Rectangle(int w, int h) : width(w), height(h) {}

        int area() const {
            return width * height;
        }
    };

    int main() {
        Rectangle rect(10, 20);
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis:")
    analyze_code(source, show_symbol_table=True)


def example_namespace():
    """Test namespace analysis."""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Namespace Analysis")
    print("=" * 80)

    source = """
    namespace math {
        int add(int a, int b) {
            return a + b;
        }

        int multiply(int a, int b) {
            return a * b;
        }
    }

    int main() {
        int x = 5;
        int y = 10;
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis:")
    analyze_code(source, show_symbol_table=True)


def example_break_continue():
    """Test break/continue validation."""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Break/Continue Validation")
    print("=" * 80)

    # Valid break
    source1 = """
    int main() {
        for (int i = 0; i < 10; i++) {
            if (i == 5) {
                break;
            }
        }
        return 0;
    }
    """

    print("\nValid break:")
    print(source1)
    print("\nAnalysis:")
    analyze_code(source1)

    # Invalid break
    source2 = """
    int main() {
        if (true) {
            break;  // Not in loop!
        }
        return 0;
    }
    """

    print("\n\nInvalid break (should fail):")
    print(source2)
    print("\nAnalysis:")
    analyze_code(source2)


def example_return_type():
    """Test return type checking."""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Return Type Checking")
    print("=" * 80)

    # Correct return type
    source1 = """
    int getValue() {
        return 42;
    }
    """

    print("\nCorrect return type:")
    print(source1)
    print("\nAnalysis:")
    analyze_code(source1)

    # Void function with return value
    source2 = """
    void doNothing() {
        return 42;  // Error: void function returns value
    }
    """

    print("\n\nVoid function with return value (should fail):")
    print(source2)
    print("\nAnalysis:")
    analyze_code(source2)


def example_enum():
    """Test enum analysis."""
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Enum Analysis")
    print("=" * 80)

    source = """
    enum Color {
        RED,
        GREEN,
        BLUE
    };

    int main() {
        Color c = RED;
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis:")
    analyze_code(source, show_symbol_table=True)


def example_function_overload():
    """Test function overloading."""
    print("\n" + "=" * 80)
    print("EXAMPLE 11: Function Overloading")
    print("=" * 80)

    source = """
    int add(int a, int b) {
        return a + b;
    }

    double add(double a, double b) {
        return a + b;
    }

    int main() {
        int x = add(5, 10);
        double y = add(5.5, 10.5);
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis:")
    analyze_code(source, show_symbol_table=True)


def example_inheritance():
    """Test class inheritance."""
    print("\n" + "=" * 80)
    print("EXAMPLE 12: Class Inheritance")
    print("=" * 80)

    source = """
    class Animal {
    public:
        int age;

        void eat() {
            return;
        }
    };

    class Dog : public Animal {
    public:
        void bark() {
            return;
        }
    };

    int main() {
        Dog d;
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis:")
    analyze_code(source, show_symbol_table=True)


def example_complex_program():
    """Test complete program with multiple features."""
    print("\n" + "=" * 80)
    print("EXAMPLE 13: Complex Program")
    print("=" * 80)

    source = """
    namespace utils {
        int abs(int x) {
            if (x < 0) {
                return -x;
            }
            return x;
        }
    }

    class Calculator {
    private:
        int result;

    public:
        Calculator() : result(0) {}

        void add(int x) {
            result = result + x;
        }

        void subtract(int x) {
            result = result - x;
        }

        int getResult() const {
            return result;
        }
    };

    int main() {
        Calculator calc;

        for (int i = 0; i < 10; i++) {
            calc.add(i);
        }

        int value = calc.getResult();
        return value;
    }
    """

    print("\nSource Code:")
    print(source)
    print("\nAnalysis:")
    analyze_code(source, show_symbol_table=True)


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("SEMANTIC ANALYZER EXAMPLES")
    print("=" * 80)

    examples = [
        ("1", "Basic Semantic Analysis", example_basic),
        ("2", "Undeclared Variable Error", example_undeclared_variable),
        ("3", "Type Mismatch Error", example_type_mismatch),
        ("4", "Redefinition Error", example_redefinition),
        ("5", "Scope Resolution", example_scope),
        ("6", "Class Analysis", example_class),
        ("7", "Namespace Analysis", example_namespace),
        ("8", "Break/Continue Validation", example_break_continue),
        ("9", "Return Type Checking", example_return_type),
        ("10", "Enum Analysis", example_enum),
        ("11", "Function Overloading", example_function_overload),
        ("12", "Class Inheritance", example_inheritance),
        ("13", "Complex Program", example_complex_program),
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
        print("\nUsage: python test_semantic.py [example_number]")
        print("   or: python test_semantic.py all\n")

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