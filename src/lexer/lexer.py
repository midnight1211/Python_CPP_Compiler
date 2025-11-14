"""
Lexical Analyzer (Lexer) for C++.
Converts source code into a stream of tokens.
"""

from typing import List, Optional
from .token import Token
from .token_types import TokenType, KEYWORDS


class LexerError(Exception):
    """Exception raised for lexical analysis errors."""

    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at {line}:{column}: {message}")


class Lexer:
    """
    Lexical analyzer that converts source code into tokens.

    This lexer supports the full C++ language syntax including:
    - All C++ keywords (C++20)
    - Integer, floating-point, character, and string literals
    - All operators and delimiters
    - Single-line and multi-line comments
    - Preprocessor directives
    """

    def __init__(self, source_code: str, filename: str = "<stdin>"):
        """
        Initialize the lexer with source code.

        Args:
            source_code: The C++ source code to tokenize
            filename: Name of the source file (for error reporting)
        """
        self.source = source_code
        self.filename = filename
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if source_code else None

    def error(self, message: str) -> None:
        """Raise a lexer error with current position information."""
        raise LexerError(message, self.line, self.column)

    def advance(self) -> None:
        """Move to the next character in the source code."""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.position += 1
        if self.position < len(self.source):
            self.current_char = self.source[self.position]
        else:
            self.current_char = None

    def peek(self, offset: int = 1) -> Optional[str]:
        """
        Look ahead at future characters without advancing.

        Args:
            offset: How many characters ahead to look

        Returns:
            The character at position + offset, or None if out of bounds
        """
        peek_pos = self.position + offset
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None

    def skip_whitespace(self) -> None:
        """Skip whitespace characters (spaces, tabs, newlines)."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_single_line_comment(self) -> None:
        """Skip single-line comments starting with //"""
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            if self.current_char == '\n':
                self.advance()

    def skip_multi_line_comment(self) -> None:
        """Skip multi-line comments /* ... */"""
        if self.current_char == '/' and self.peek() == '*':
            start_line = self.line
            start_column = self.column

            self.advance()  # Skip /
            self.advance()  # Skip *

            while self.current_char is not None:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()  # Skip *
                    self.advance()  # Skip /
                    return
                self.advance()

            raise LexerError(
                f"Unterminated comment starting at {start_line}:{start_column}",
                self.line,
                self.column
            )

    def read_preprocessor(self) -> Token:
        """Read preprocessor directives like #include, #define"""
        start_line = self.line
        start_column = self.column
        directive = ''

        while self.current_char is not None:
            if self.current_char == '\\' and self.peek() == '\n':
                directive += self.current_char
                self.advance()
                directive += self.current_char
                self.advance()
            elif self.current_char == '\n':
                break
            else:
                directive += self.current_char
                self.advance()

        return Token(TokenType.PREPROCESSOR, directive, start_line, start_column)

    def read_number(self) -> Token:
        """Read integer or floating-point literals."""
        start_line = self.line
        start_column = self.column
        num_str = ''
        is_float = False

        # Handle hexadecimal literals (0x or 0X)
        if self.current_char == '0' and self.peek() in ['x', 'X']:
            num_str += self.current_char
            self.advance()
            num_str += self.current_char
            self.advance()

            if not self.current_char or self.current_char not in '0123456789abcdefABCDEF':
                self.error("Invalid hexadecimal literal")

            while self.current_char and self.current_char in '0123456789abcdefABCDEF\'':
                if self.current_char != '\'':
                    num_str += self.current_char
                self.advance()

            while self.current_char and self.current_char in 'uUlL':
                num_str += self.current_char
                self.advance()

            return Token(TokenType.INTEGER, num_str, start_line, start_column)

        # Handle binary literals (0b or 0B)
        if self.current_char == '0' and self.peek() in ['b', 'B']:
            num_str += self.current_char
            self.advance()
            num_str += self.current_char
            self.advance()

            if not self.current_char or self.current_char not in '01':
                self.error("Invalid binary literal")

            while self.current_char and self.current_char in '01\'':
                if self.current_char != '\'':
                    num_str += self.current_char
                self.advance()

            while self.current_char and self.current_char in 'uUlL':
                num_str += self.current_char
                self.advance()

            return Token(TokenType.INTEGER, num_str, start_line, start_column)

        # Handle octal literals
        if self.current_char == '0' and self.peek() and self.peek().isdigit():
            num_str += self.current_char
            self.advance()

            while self.current_char and self.current_char in '01234567\'':
                if self.current_char != '\'':
                    num_str += self.current_char
                self.advance()

            while self.current_char and self.current_char in 'uUlL':
                num_str += self.current_char
                self.advance()

            return Token(TokenType.INTEGER, num_str, start_line, start_column)

        # Read decimal digits
        while self.current_char and (self.current_char.isdigit() or self.current_char == '\''):
            if self.current_char != '\'':
                num_str += self.current_char
            self.advance()

        # Check for decimal point
        if self.current_char == '.' and self.peek() and (self.peek().isdigit() or self.peek() in 'eE'):
            is_float = True
            num_str += self.current_char
            self.advance()

            while self.current_char and (self.current_char.isdigit() or self.current_char == '\''):
                if self.current_char != '\'':
                    num_str += self.current_char
                self.advance()

        # Check for exponent
        if self.current_char in ['e', 'E']:
            is_float = True
            num_str += self.current_char
            self.advance()

            if self.current_char in ['+', '-']:
                num_str += self.current_char
                self.advance()

            if not self.current_char or not self.current_char.isdigit():
                self.error("Invalid exponent in floating-point literal")

            while self.current_char and self.current_char.isdigit():
                num_str += self.current_char
                self.advance()

        # Check for suffixes
        if self.current_char in 'fFlL':
            is_float = True
            num_str += self.current_char
            self.advance()

        if not is_float:
            while self.current_char and self.current_char in 'uUlL':
                num_str += self.current_char
                self.advance()

        token_type = TokenType.FLOAT_LITERAL if is_float else TokenType.INTEGER
        return Token(token_type, num_str, start_line, start_column)

    def read_char_literal(self) -> Token:
        """Read character literals like 'a' or '\\n'"""
        start_line = self.line
        start_column = self.column
        char_str = self.current_char
        self.advance()

        if self.current_char is None:
            self.error("Unterminated character literal")

        if self.current_char == '\\':
            char_str += self.current_char
            self.advance()
            if self.current_char is None:
                self.error("Unterminated character literal")
            char_str += self.current_char
            self.advance()
        elif self.current_char == "'":
            self.error("Empty character literal")
        else:
            char_str += self.current_char
            self.advance()

        if self.current_char != "'":
            self.error("Unterminated character literal")
        char_str += self.current_char
        self.advance()

        return Token(TokenType.CHAR_LITERAL, char_str, start_line, start_column)

    def read_string_literal(self) -> Token:
        """Read string literals like \"hello\" """
        start_line = self.line
        start_column = self.column
        string_str = self.current_char
        self.advance()

        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                string_str += self.current_char
                self.advance()
                if self.current_char is None:
                    self.error("Unterminated string literal")
                string_str += self.current_char
                self.advance()
            elif self.current_char == '\n':
                self.error("Unterminated string literal (newline in string)")
            else:
                string_str += self.current_char
                self.advance()

        if self.current_char is None:
            self.error("Unterminated string literal")

        string_str += self.current_char
        self.advance()

        return Token(TokenType.STRING_LITERAL, string_str, start_line, start_column)

    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_line = self.line
        start_column = self.column
        id_str = ''

        while (self.current_char is not None and
               (self.current_char.isalnum() or self.current_char == '_')):
            id_str += self.current_char
            self.advance()

        token_type = KEYWORDS.get(id_str, TokenType.IDENTIFIER)
        return Token(token_type, id_str, start_line, start_column)

    def get_next_token(self) -> Token:
        """Get the next token from the source code."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                return self.read_preprocessor()

            if self.current_char == '/':
                if self.peek() == '/':
                    self.skip_single_line_comment()
                    continue
                elif self.peek() == '*':
                    self.skip_multi_line_comment()
                    continue

            if self.current_char.isdigit():
                return self.read_number()

            if self.current_char == "'":
                return self.read_char_literal()

            if self.current_char == '"':
                return self.read_string_literal()

            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()

            start_line = self.line
            start_column = self.column

            # Three-character operators
            three_char = self.current_char + (self.peek() or '') + (self.peek(2) or '')
            if three_char == '<=>':
                self.advance()
                self.advance()
                self.advance()
                return Token(TokenType.SPACESHIP, '<=>', start_line, start_column)

            if three_char == '...':
                self.advance()
                self.advance()
                self.advance()
                return Token(TokenType.ELLIPSIS, '...', start_line, start_column)

            if three_char == '>>=':
                self.advance()
                self.advance()
                self.advance()
                return Token(TokenType.RIGHT_SHIFT_ASSIGN, '>>=', start_line, start_column)

            if three_char == '<<=':
                self.advance()
                self.advance()
                self.advance()
                return Token(TokenType.LEFT_SHIFT_ASSIGN, '<<=', start_line, start_column)

            if three_char == '->*':
                self.advance()
                self.advance()
                self.advance()
                return Token(TokenType.ARROW_STAR, '->*', start_line, start_column)

            # Two-character operators
            two_char_ops = {
                '==': TokenType.EQUAL, '!=': TokenType.NOT_EQUAL,
                '<=': TokenType.LESS_EQUAL, '>=': TokenType.GREATER_EQUAL,
                '&&': TokenType.LOGICAL_AND, '||': TokenType.LOGICAL_OR,
                '++': TokenType.INCREMENT, '--': TokenType.DECREMENT,
                '->': TokenType.ARROW, '::': TokenType.SCOPE,
                '<<': TokenType.LEFT_SHIFT, '>>': TokenType.RIGHT_SHIFT,
                '+=': TokenType.PLUS_ASSIGN, '-=': TokenType.MINUS_ASSIGN,
                '*=': TokenType.MULTIPLY_ASSIGN, '/=': TokenType.DIVIDE_ASSIGN,
                '%=': TokenType.MODULO_ASSIGN, '&=': TokenType.AND_ASSIGN,
                '|=': TokenType.OR_ASSIGN, '^=': TokenType.XOR_ASSIGN,
                '.*': TokenType.DOT_STAR,
            }

            two_char = self.current_char + (self.peek() or '')
            if two_char in two_char_ops:
                self.advance()
                self.advance()
                return Token(two_char_ops[two_char], two_char, start_line, start_column)

            # Single-character tokens
            single_char_tokens = {
                '+': TokenType.PLUS, '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY, '/': TokenType.DIVIDE,
                '%': TokenType.MODULO, '=': TokenType.ASSIGN,
                '<': TokenType.LESS_THAN, '>': TokenType.GREATER_THAN,
                '!': TokenType.LOGICAL_NOT, '&': TokenType.BITWISE_AND,
                '|': TokenType.BITWISE_OR, '^': TokenType.BITWISE_XOR,
                '~': TokenType.BITWISE_NOT, '.': TokenType.DOT,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
                ';': TokenType.SEMICOLON, ',': TokenType.COMMA,
                ':': TokenType.COLON, '?': TokenType.QUESTION,
            }

            if self.current_char in single_char_tokens:
                char = self.current_char
                token_type = single_char_tokens[char]
                self.advance()
                return Token(token_type, char, start_line, start_column)

            char = self.current_char
            self.advance()
            self.error(f"Invalid character: '{char}'")

        return Token(TokenType.EOF, '', self.line, self.column)

    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code and return a list of tokens."""
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens