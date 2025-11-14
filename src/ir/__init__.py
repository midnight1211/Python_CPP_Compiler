"""
Intermediate Representation (IR) package for the C++ compiler.

This package contains the IR generation and optimization components:
- IR instructions: Three-address code instruction set
- IR generator: Converts AST to IR
- IR optimizer: Performs optimization passes

Example usage:
    from src.lexer import Lexer
    from src.parser import Parser
    from src.semantic import SemanticAnalyzer
    from src.ir import IRGenerator, optimize_ir

    source_code = '''
    int add(int a, int b) {
        return a + b;
    }

    int main() {
        int x = 5;
        int y = 10;
        int result = add(x, y);
        return result;
    }
    '''

    # Lex, parse, and analyze
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    # Generate IR
    ir_gen = IRGenerator()
    ir_program = ir_gen.generate(ast)

    # Optimize
    optimized = optimize_ir(ir_program, level=2)

    # Print IR
    print(optimized)
"""

from .ir_instructions import (
    IROpcode,
    IRValue,
    IRTemp,
    IRConstant,
    IRVariable,
    IRLabel,
    IRInstruction,
    IRFunction,
    IRProgram,
    IRBuilder
)
from .ir_generator import IRGenerator, IRGeneratorError
from .ir_optimizer import (
    IROptimizer,
    PeepholeOptimizer,
    optimize_ir
)

__all__ = [
    # Instructions
    'IROpcode',
    'IRValue',
    'IRTemp',
    'IRConstant',
    'IRVariable',
    'IRLabel',
    'IRInstruction',
    'IRFunction',
    'IRProgram',
    'IRBuilder',

    # Generator
    'IRGenerator',
    'IRGeneratorError',

    # Optimizer
    'IROptimizer',
    'PeepholeOptimizer',
    'optimize_ir',
]

__version__ = '1.0.0'
__author__ = 'David Vuksanovich'
__description__ = 'Intermediate representation for C++ compiler'