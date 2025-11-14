"""
Token representation for the lexer.
Contains the Token class which represents a single lexical token
"""

from dataclasses import dataclass
from typing import Any
from .token_types import TokenType

@dataclass
class Token:
    """
    Represents a single token in the source code.

    Attributes:
        type: The type of token (keyword, identifier, operator, etc.)
        value: The actual text value of the token.
        line: Line number where the token appears.
        column: Column number where the token starts.
    """
    type: TokenType
    value: str
    line: int
    column: int

    def __repr(self) -> str:
        """Return a string representation of the token."""
        return f"Token({self.type.name}, '{self.value}', '{self.line}:{self.column})"

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"{self.type.name}('{self.value}')"

    def is_keyword(self) -> bool:
        """Check if this token is a keyword."""
        keyword_types = {
            TokenType.IF, TokenType.ELSE, TokenType.SWITCH, TokenType.CASE,
            TokenType.DEFAULT, TokenType.WHILE, TokenType.DO, TokenType.FOR,
            TokenType.BREAK, TokenType.CONTINUE, TokenType.RETURN, TokenType.GOTO,
            TokenType.VOID, TokenType.BOOL, TokenType.CHAR, TokenType.INT,
            TokenType.SHORT, TokenType.LONG, TokenType.SIGNED, TokenType.UNSIGNED,
            TokenType.FLOAT, TokenType.DOUBLE, TokenType.CONST, TokenType.VOLATILE,
            TokenType.MUTABLE, TokenType.CONSTEXPR, TokenType.AUTO, TokenType.REGISTER,
            TokenType.STATIC, TokenType.EXTERN, TokenType.CLASS, TokenType.STRUCT,
            TokenType.UNION, TokenType.ENUM, TokenType.PUBLIC, TokenType.PRIVATE,
            TokenType.PROTECTED, TokenType.FRIEND, TokenType.VIRTUAL, TokenType.THIS,
            TokenType.OPERATOR, TokenType.SIZEOF, TokenType.TYPEID, TokenType.TYPENAME,
            TokenType.NEW, TokenType.DELETE, TokenType.TRY, TokenType.CATCH,
            TokenType.THROW, TokenType.TEMPLATE, TokenType.NAMESPACE, TokenType.USING,
            TokenType.TYPEDEF, TokenType.EXPLICIT, TokenType.INLINE, TokenType.NULLPTR,
        }
        return self.type in keyword_types

    def is_operator(self) -> bool:
        """Check if this token is an operator."""
        operator_types = {
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.MODULO, TokenType.INCREMENT, TokenType.DECREMENT,
            TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
            TokenType.MULTIPLY_ASSIGN, TokenType.DIVIDE_ASSIGN, TokenType.MODULO_ASSIGN,
            TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN,
            TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
            TokenType.LOGICAL_AND, TokenType.LOGICAL_OR, TokenType.LOGICAL_NOT,
            TokenType.BITWISE_AND, TokenType.BITWISE_OR, TokenType.BITWISE_XOR,
            TokenType.BITWISE_NOT, TokenType.LEFT_SHIFT, TokenType.RIGHT_SHIFT,
            TokenType.DOT, TokenType.ARROW, TokenType.SCOPE,
        }
        return self.type in operator_types

    def is_literal(self) -> bool:
        """Check if this token is a literal value."""
        literal_types = {
            TokenType.INTEGER, TokenType.FLOAT_LITERAL,
            TokenType.CHAR_LITERAL, TokenType.STRING_LITERAL,
            TokenType.TRUE, TokenType.FALSE, TokenType.NULLPTR,
        }
        return self.type in literal_types

    def is_delimiter(self) -> bool:
        """Check if this token is a delimiter."""
        delimiter_types = {
            TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LBRACKET, TokenType.RBRACKET, TokenType.SEMICOLON,
            TokenType.COMMA, TokenType.COLON,
        }
        return self.type in delimiter_types

    def is_type(self) -> bool:
        """Check if this token represents a type."""
        type_keywords = {
            TokenType.VOID, TokenType.BOOL, TokenType.CHAR, TokenType.INT,
            TokenType.SHORT, TokenType.LONG, TokenType.SIGNED, TokenType.UNSIGNED,
            TokenType.FLOAT, TokenType.DOUBLE, TokenType.WCHAR_T,
            TokenType.CHAR8_T, TokenType.CHAR16_T, TokenType.CHAR32_T,
            TokenType.AUTO,
        }
        return self.type in type_keywords

    def matches(self, token_type: TokenType) -> bool:
        """Check if this token matches a specific type."""
        return self.type == token_type

    def matches_any(self, *token_types: TokenType) -> bool:
        """Check if this token matches any of the given types."""
        return self.type in token_types