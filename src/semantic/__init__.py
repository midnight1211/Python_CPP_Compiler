"""
Semantic Analysis package for the C++ compiler.

This package contains the semantic analysis components:
- SemanticAnalyzer: Main semantic analyzer
- SymbolTable: Symbol table with scope management
- TypeChecker: Type checking and inference
- TypeRegistry: User-defined type tracking

Example usage:
    from src.lexer import Lexer
    from src.parser import Parser
    from src.semantic import SemanticAnalyzer

    source_code = '''
    int main() {
        int x = 5;
        return x * 2;
    }
    '''

    # Lex and parse
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    # Semantic analysis
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)

    if success:
        print("Semantic analysis passed")
    else:
        analyzer.print_errors()
"""

from .analyzer import SemanticAnalyzer, SemanticError
from .symbol_table import (
    SymbolTable,
    Symbol,
    SymbolKind,
    Scope,
    FunctionSignature,
    TypeRegistry
)
from .type_checker import TypeChecker, TypeCheckError

__all__ = [
    # Main analyzer
    'SemanticAnalyzer',
    'SemanticError',

    # Symbol table
    'SymbolTable',
    'Symbol',
    'SymbolKind',
    'Scope',
    'FunctionSignature',
    'TypeRegistry',

    # Type checker
    'TypeChecker',
    'TypeCheckError',
]

__version__ = '1.0.0'
__author__ = 'David Vuksanovich'
__description__ = 'Semantic analyzer for C++ compiler'