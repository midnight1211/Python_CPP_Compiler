"""
Code Generation package for the C++ compiler.

This package contains the code generation components:
- CodeGenerator: Main code generator (IR to assembly)
- RegisterAllocator: Register allocation algorithms

Example usage:
    from src.lexer import Lexer
    from src.parser import Parser
    from src.semantic import SemanticAnalyzer
    from src.ir import IRGenerator, optimize_ir
    from src.codegen import CodeGenerator

    source_code = '''
    int add(int a, int b) {
        return a + b;
    }

    int main() {
        int result = add(5, 10);
        return result;
    }
    '''

    # Full compilation pipeline
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    ir_gen = IRGenerator()
    ir_program = ir_gen.generate(ast)

    optimized = optimize_ir(ir_program, level=2)

    codegen = CodeGenerator(target="x86_64")
    assembly = codegen.generate(optimized)

    print(assembly)
"""

from .code_generator import CodeGenerator, CodeGeneratorError
from .register_allocator import (
    RegisterAllocator,
    GraphColoringAllocator,
    LiveRange,
    allocate_registers
)

__all__ = [
    # Code generator
    'CodeGenerator',
    'CodeGeneratorError',

    # Register allocation
    'RegisterAllocator',
    'GraphColoringAllocator',
    'LiveRange',
    'allocate_registers',
]

__version__ = '1.0.0'
__author__ = 'Your Name'
__description__ = 'Code generator for C++ compiler'