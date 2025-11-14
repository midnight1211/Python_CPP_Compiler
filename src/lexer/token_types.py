"""
Token types for the C++ lexer.
Defines all possible token types in the C++ language.
"""

from enum import Enum, auto


class TokenType(Enum):
    """Enumeration of all token types in C++."""

    # C++ Keywords - Control Flow
    IF = auto()
    ELSE = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    WHILE = auto()
    DO = auto()
    FOR = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    GOTO = auto()

    # C++ Keywords - Data Types
    VOID = auto()
    BOOL = auto()
    CHAR = auto()
    INT = auto()
    SHORT = auto()
    LONG = auto()
    SIGNED = auto()
    UNSIGNED = auto()
    FLOAT = auto()
    DOUBLE = auto()
    WCHAR_T = auto()
    CHAR8_T = auto()
    CHAR16_T = auto()
    CHAR32_T = auto()

    # C++ Keywords - Type Modifiers
    CONST = auto()
    VOLATILE = auto()
    MUTABLE = auto()
    CONSTEXPR = auto()
    CONSTEVAL = auto()
    CONSTINIT = auto()

    # C++ Keywords - Storage Class
    AUTO = auto()
    REGISTER = auto()
    STATIC = auto()
    EXTERN = auto()
    THREAD_LOCAL = auto()

    # C++ Keywords - Object-Oriented
    CLASS = auto()
    STRUCT = auto()
    UNION = auto()
    ENUM = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()
    FRIEND = auto()
    VIRTUAL = auto()
    OVERRIDE = auto()
    FINAL = auto()

    # C++ Keywords - Inheritance & Polymorphism
    THIS = auto()
    OPERATOR = auto()
    SIZEOF = auto()
    TYPEID = auto()
    TYPENAME = auto()

    # C++ Keywords - Memory Management
    NEW = auto()
    DELETE = auto()

    # C++ Keywords - Exception Handling
    TRY = auto()
    CATCH = auto()
    THROW = auto()
    NOEXCEPT = auto()

    # C++ Keywords - Templates
    TEMPLATE = auto()
    EXPORT = auto()

    # C++ Keywords - Namespaces
    NAMESPACE = auto()
    USING = auto()

    # C++ Keywords - Type Casting
    STATIC_CAST = auto()
    DYNAMIC_CAST = auto()
    CONST_CAST = auto()
    REINTERPRET_CAST = auto()

    # C++ Keywords - Other
    TYPEDEF = auto()
    ASM = auto()
    EXPLICIT = auto()
    INLINE = auto()
    STATIC_ASSERT = auto()
    DECLTYPE = auto()
    ALIGNAS = auto()
    ALIGNOF = auto()
    NULLPTR = auto()

    # C++ Keywords - Concepts & Requires (C++20)
    CONCEPT = auto()
    REQUIRES = auto()
    CO_AWAIT = auto()
    CO_RETURN = auto()
    CO_YIELD = auto()

    # Boolean Literals
    TRUE = auto()
    FALSE = auto()

    # Identifiers and literals
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT_LITERAL = auto()
    CHAR_LITERAL = auto()
    STRING_LITERAL = auto()

    # Operators - Arithmetic
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    INCREMENT = auto()
    DECREMENT = auto()

    # Operators - Assignment
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    MULTIPLY_ASSIGN = auto()
    DIVIDE_ASSIGN = auto()
    MODULO_ASSIGN = auto()
    AND_ASSIGN = auto()
    OR_ASSIGN = auto()
    XOR_ASSIGN = auto()
    LEFT_SHIFT_ASSIGN = auto()
    RIGHT_SHIFT_ASSIGN = auto()

    # Operators - Comparison
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    SPACESHIP = auto()  # <=> (C++20)

    # Operators - Logical
    LOGICAL_AND = auto()
    LOGICAL_OR = auto()
    LOGICAL_NOT = auto()

    # Operators - Bitwise
    BITWISE_AND = auto()
    BITWISE_OR = auto()
    BITWISE_XOR = auto()
    BITWISE_NOT = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()

    # Operators - Member Access
    DOT = auto()
    ARROW = auto()
    SCOPE = auto()  # ::
    DOT_STAR = auto()  # .*
    ARROW_STAR = auto()  # ->*

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    COLON = auto()
    QUESTION = auto()
    ELLIPSIS = auto()  # ...

    # Preprocessor (basic recognition)
    PREPROCESSOR = auto()

    # Special
    EOF = auto()
    INVALID = auto()


# Mapping of C++ keywords to their token types
KEYWORDS = {
    # Control Flow
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'switch': TokenType.SWITCH,
    'case': TokenType.CASE,
    'default': TokenType.DEFAULT,
    'while': TokenType.WHILE,
    'do': TokenType.DO,
    'for': TokenType.FOR,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'return': TokenType.RETURN,
    'goto': TokenType.GOTO,

    # Data Types
    'void': TokenType.VOID,
    'bool': TokenType.BOOL,
    'char': TokenType.CHAR,
    'int': TokenType.INT,
    'short': TokenType.SHORT,
    'long': TokenType.LONG,
    'signed': TokenType.SIGNED,
    'unsigned': TokenType.UNSIGNED,
    'float': TokenType.FLOAT,
    'double': TokenType.DOUBLE,
    'wchar_t': TokenType.WCHAR_T,
    'char8_t': TokenType.CHAR8_T,
    'char16_t': TokenType.CHAR16_T,
    'char32_t': TokenType.CHAR32_T,

    # Type Modifiers
    'const': TokenType.CONST,
    'volatile': TokenType.VOLATILE,
    'mutable': TokenType.MUTABLE,
    'constexpr': TokenType.CONSTEXPR,
    'consteval': TokenType.CONSTEVAL,
    'constinit': TokenType.CONSTINIT,

    # Storage Class
    'auto': TokenType.AUTO,
    'register': TokenType.REGISTER,
    'static': TokenType.STATIC,
    'extern': TokenType.EXTERN,
    'thread_local': TokenType.THREAD_LOCAL,

    # Object-Oriented
    'class': TokenType.CLASS,
    'struct': TokenType.STRUCT,
    'union': TokenType.UNION,
    'enum': TokenType.ENUM,
    'public': TokenType.PUBLIC,
    'private': TokenType.PRIVATE,
    'protected': TokenType.PROTECTED,
    'friend': TokenType.FRIEND,
    'virtual': TokenType.VIRTUAL,
    'override': TokenType.OVERRIDE,
    'final': TokenType.FINAL,

    # Other Keywords
    'this': TokenType.THIS,
    'operator': TokenType.OPERATOR,
    'sizeof': TokenType.SIZEOF,
    'typeid': TokenType.TYPEID,
    'typename': TokenType.TYPENAME,
    'new': TokenType.NEW,
    'delete': TokenType.DELETE,
    'try': TokenType.TRY,
    'catch': TokenType.CATCH,
    'throw': TokenType.THROW,
    'noexcept': TokenType.NOEXCEPT,
    'template': TokenType.TEMPLATE,
    'export': TokenType.EXPORT,
    'namespace': TokenType.NAMESPACE,
    'using': TokenType.USING,
    'static_cast': TokenType.STATIC_CAST,
    'dynamic_cast': TokenType.DYNAMIC_CAST,
    'const_cast': TokenType.CONST_CAST,
    'reinterpret_cast': TokenType.REINTERPRET_CAST,
    'typedef': TokenType.TYPEDEF,
    'asm': TokenType.ASM,
    'explicit': TokenType.EXPLICIT,
    'inline': TokenType.INLINE,
    'static_assert': TokenType.STATIC_ASSERT,
    'decltype': TokenType.DECLTYPE,
    'alignas': TokenType.ALIGNAS,
    'alignof': TokenType.ALIGNOF,
    'nullptr': TokenType.NULLPTR,
    'concept': TokenType.CONCEPT,
    'requires': TokenType.REQUIRES,
    'co_await': TokenType.CO_AWAIT,
    'co_return': TokenType.CO_RETURN,
    'co_yield': TokenType.CO_YIELD,

    # Boolean Literals
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
}