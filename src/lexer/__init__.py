"""
Lexer package for the C++ compiler.

This package contains the lexical analysis components:
- Lexer: The main lexical analyzer
- Token: Token representation
- TokenType: Enumeration of all token types
- KEYWORDS: Mapping of keywords to token types

Example usage:
    from src.lexer import Lexer, Token, TokenType

    source_code = '''
    int main() {
        return 0;
    }
    '''

    lexer = Lexer(source_code, "main.cpp")
    tokens = lexer.tokenize()

    for token in tokens:
        print(token)
"""

from .lexer import Lexer, LexerError
from .token import Token
from .token_types import TokenType, KEYWORDS

__all__ = [
    'Lexer',
    'LexerError',
    'Token',
    'TokenType',
    'KEYWORDS',
]

__version__ = '1.0.0'
__author__ = 'David Vuksanovich'
__description__ = 'Lexical analyzer for C++ compiler'