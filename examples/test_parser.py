"""
Example usage and testing of the C++ parser.
Demonstrates how to parse C++ code and work with the AST.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer import Lexer, LexerError
from src.parser import Parser, ParserError


def print_ast(node, indent=0):
    """Pretty print the AST."""
    prefix = "  " * indent
    node_type = type(node).__name__
    print(f"{prefix}{node_type}")

    # Print node attributes
    if hasattr(node, '__dataclass_fields__'):
        for field_name, field_value in node.__dict__.items():
            if field_value is None:
                continue

            if isinstance(field_value, list):
                if field_value:
                    print(f"{prefix}  {field_name}:")
                    for item in field_value:
                        if hasattr(item, '__dataclass_fields__'):
                            print_ast(item, indent + 2)
                        else:
                            print(f"{prefix}    {item}")
            elif hasattr(field_value, '__dataclass_fields__'):
                print(f"{prefix}  {field_name}:")
                print_ast(field_value, indent + 2)
            else:
                print(f"{prefix}  {field_name}: {field_value}")


def example_basic():
    """Basic parsing example."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Function")
    print("="*80)

    source = """
    int add(int a, int b) {
        return a + b;
    }
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print("\nAST:")
        print_ast(ast)

        print(f"\n✓ Successfully parsed {len(ast.declarations)} declaration(s)")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_class():
    """Parse a class."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Class Definition")
    print("="*80)

    source = """
    class Rectangle {
    public:
        Rectangle(int w, int h) : width(w), height(h) {}
        
        int area() const {
            return width * height;
        }
        
    private:
        int width;
        int height;
    };
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print("\nAST:")
        print_ast(ast)

        # Access class details
        class_decl = ast.declarations[0]
        print(f"\n✓ Parsed class: {class_decl.name}")
        print(f"  Members: {len(class_decl.members)}")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_control_flow():
    """Parse control flow statements."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Control Flow")
    print("="*80)

    source = """
    int factorial(int n) {
        if (n <= 1) {
            return 1;
        } else {
            return n * factorial(n - 1);
        }
    }
    
    int fibonacci(int n) {
        int a = 0;
        int b = 1;
        
        for (int i = 0; i < n; i++) {
            int temp = a;
            a = b;
            b = temp + b;
        }
        
        return a;
    }
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print(f"\n✓ Parsed {len(ast.declarations)} function(s)")
        for decl in ast.declarations:
            print(f"  - {decl.name}()")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_template():
    """Parse template."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Template")
    print("="*80)

    source = """
    template<typename T>
    T maximum(T a, T b) {
        if (a > b) {
            return a;
        } else {
            return b;
        }
    }
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print("\nAST:")
        print_ast(ast)

        template_decl = ast.declarations[0]
        print(f"\n✓ Parsed template with {len(template_decl.template_parameters)} parameter(s)")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_namespace():
    """Parse namespace."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Namespace")
    print("="*80)

    source = """
    namespace math {
        int add(int a, int b) {
            return a + b;
        }
        
        int subtract(int a, int b) {
            return a - b;
        }
    }
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        namespace_decl = ast.declarations[0]
        print(f"\n✓ Parsed namespace: {namespace_decl.name}")
        print(f"  Contains {len(namespace_decl.declarations)} declaration(s)")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_expressions():
    """Parse complex expressions."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Complex Expressions")
    print("="*80)

    source = """
    int calculate() {
        int x = 5;
        int y = 10;
        
        int sum = x + y * 2;
        int result = (x > y) ? x : y;
        
        x += 5;
        y++;
        
        return sum + result;
    }
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print("\n✓ Successfully parsed complex expressions")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_pointers():
    """Parse pointers and references."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Pointers and References")
    print("="*80)

    source = """
    void swap(int* a, int* b) {
        int temp = *a;
        *a = *b;
        *b = temp;
    }
    
    void increment(int& value) {
        value++;
    }
    
    int* createArray(int size) {
        return new int[size];
    }
    
    void deleteArray(int* arr) {
        delete[] arr;
    }
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print(f"\n✓ Parsed {len(ast.declarations)} function(s) with pointers/references")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_enum():
    """Parse enum."""
    print("\n" + "="*80)
    print("EXAMPLE 8: Enum")
    print("="*80)

    source = """
    enum Color {
        RED,
        GREEN,
        BLUE
    };
    
    enum class Status {
        SUCCESS = 0,
        ERROR = 1,
        PENDING = 2
    };
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print(f"\n✓ Parsed {len(ast.declarations)} enum(s)")
        for decl in ast.declarations:
            print(f"  - {decl.name} with {len(decl.enumerators)} enumerator(s)")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_error_handling():
    """Parse try-catch."""
    print("\n" + "="*80)
    print("EXAMPLE 9: Exception Handling")
    print("="*80)

    source = """
    void processData(int value) {
        try {
            if (value < 0) {
                throw -1;
            }
            
            int result = 100 / value;
            
        } catch (int e) {
            return;
        }
    }
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print("\n✓ Successfully parsed try-catch block")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_full_program():
    """Parse a complete program."""
    print("\n" + "="*80)
    print("EXAMPLE 10: Complete Program")
    print("="*80)

    source = """
    #include <iostream>
    
    namespace utils {
        template<typename T>
        class Stack {
        private:
            T* data;
            int size;
            int capacity;
            
        public:
            Stack(int cap) : capacity(cap), size(0) {
                data = new T[capacity];
            }
            
            ~Stack() {
                delete[] data;
            }
            
            void push(const T& value) {
                if (size < capacity) {
                    data[size++] = value;
                }
            }
            
            T pop() {
                if (size > 0) {
                    return data[--size];
                }
                throw -1;
            }
            
            bool isEmpty() const {
                return size == 0;
            }
        };
    }
    
    int main() {
        utils::Stack<int> stack(10);
        
        for (int i = 0; i < 5; i++) {
            stack.push(i * 2);
        }
        
        while (!stack.isEmpty()) {
            int value = stack.pop();
        }
        
        return 0;
    }
    """

    print("\nSource Code:")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print(f"\n✓ Successfully parsed complete program")
        print(f"  Total declarations: {len(ast.declarations)}")

        for i, decl in enumerate(ast.declarations, 1):
            decl_type = type(decl).__name__
            if hasattr(decl, 'name'):
                print(f"  {i}. {decl_type}: {decl.name}")
            else:
                print(f"  {i}. {decl_type}")

    except (LexerError, ParserError) as e:
        print(f"\nError: {e}")


def example_syntax_error():
    """Test error handling."""
    print("\n" + "="*80)
    print("EXAMPLE 11: Syntax Error Detection")
    print("="*80)

    source = """
    int main() {
        int x = 5
        return x;
    }
    """

    print("\nSource Code (missing semicolon):")
    print(source)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        print("\n✗ Error: Should have caught syntax error!")

    except ParserError as e:
        print(f"\n✓ Correctly caught parser error:")
        print(f"  {e}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("C++ PARSER EXAMPLES")
    print("="*80)

    examples = [
        ("1", "Basic Function", example_basic),
        ("2", "Class Definition", example_class),
        ("3", "Control Flow", example_control_flow),
        ("4", "Template", example_template),
        ("5", "Namespace", example_namespace),
        ("6", "Complex Expressions", example_expressions),
        ("7", "Pointers and References", example_pointers),
        ("8", "Enum", example_enum),
        ("9", "Exception Handling", example_error_handling),
        ("10", "Complete Program", example_full_program),
        ("11", "Syntax Error Detection", example_syntax_error),
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
        print("\nUsage: python test_parser.py [example_number]")
        print("   or: python test_parser.py all\n")

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