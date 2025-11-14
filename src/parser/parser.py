"""
Recursive Descent Parser for C++.
Converts a stream of tokens into an Abstract Syntax Tree (AST).
"""

from typing import List, Optional
import sys
sys.path.append('..')

from src.lexer import Token, TokenType
from .ast_nodes import *


class ParserError(Exception):
    """Exception raised for parser errors."""

    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parser error at {token.line}:{token.column}: {message}")


class Parser:
    """
    Recursive descent parser for C++.

    Converts a stream of tokens into an Abstract Syntax Tree (AST).
    """

    def __init__(self, tokens: List[Token]):
        """
        Initialize the parser with a list of tokens.

        Args:
            tokens: List of tokens from the lexer
        """
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None

    def error(self, message: str) -> None:
        """Raise a parser error."""
        raise ParserError(message, self.current_token)

    def advance(self) -> Token:
        """Move to the next token and return the current one."""
        token = self.current_token
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        return token

    def peek(self, offset: int = 1) -> Optional[Token]:
        """Look ahead at future tokens."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type and consume it."""
        if self.current_token.type != token_type:
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name}")
        return self.advance()

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current_token.type in token_types

    def match_and_consume(self, *token_types: TokenType) -> Optional[Token]:
        """If current token matches, consume and return it."""
        if self.match(*token_types):
            return self.advance()
        return None

    # Main parsing method
    def parse(self) -> Program:
        """Parse the entire program."""
        declarations = []
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.PREPROCESSOR:
                self.advance()  # Skip preprocessor directives
                continue
            decl = self.parse_declaration()
            if decl:
                declarations.append(decl)
        return Program(declarations)

    # Declaration parsing
    def parse_declaration(self) -> Optional[Declaration]:
        """Parse a declaration."""
        # Namespace
        if self.match(TokenType.NAMESPACE):
            return self.parse_namespace()

        # Using declaration
        if self.match(TokenType.USING):
            return self.parse_using()

        # Template
        if self.match(TokenType.TEMPLATE):
            return self.parse_template()

        # Class/Struct
        if self.match(TokenType.CLASS, TokenType.STRUCT):
            return self.parse_class()

        # Enum
        if self.match(TokenType.ENUM):
            return self.parse_enum()

        # Typedef
        if self.match(TokenType.TYPEDEF):
            return self.parse_typedef()

        # Function or variable declaration
        return self.parse_function_or_variable()

    def parse_namespace(self) -> NamespaceDeclaration:
        """Parse namespace declaration."""
        self.expect(TokenType.NAMESPACE)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)

        declarations = []
        while not self.match(TokenType.RBRACE) and self.current_token.type != TokenType.EOF:
            decl = self.parse_declaration()
            if decl:
                declarations.append(decl)

        self.expect(TokenType.RBRACE)
        return NamespaceDeclaration(name, declarations)

    def parse_using(self) -> UsingDeclaration:
        """Parse using declaration."""
        self.expect(TokenType.USING)

        # Handle 'using namespace X;'
        if self.match(TokenType.NAMESPACE):
            self.advance()

        name_parts = []
        name_parts.append(self.expect(TokenType.IDENTIFIER).value)

        while self.match(TokenType.SCOPE):
            self.advance()
            name_parts.append(self.expect(TokenType.IDENTIFIER).value)

        self.expect(TokenType.SEMICOLON)
        return UsingDeclaration('::'.join(name_parts))

    def parse_template(self) -> TemplateDeclaration:
        """Parse template declaration."""
        self.expect(TokenType.TEMPLATE)
        self.expect(TokenType.LESS_THAN)

        params = []
        while not self.match(TokenType.GREATER_THAN):
            kind = self.advance().value  # 'typename' or 'class'
            name = self.expect(TokenType.IDENTIFIER).value

            default_type = None
            if self.match(TokenType.ASSIGN):
                self.advance()
                default_type = self.parse_type()

            params.append(TemplateParameter(kind, name, default_type))

            if not self.match(TokenType.GREATER_THAN):
                self.expect(TokenType.COMMA)

        self.expect(TokenType.GREATER_THAN)

        # Parse the templated declaration
        declaration = self.parse_declaration()
        return TemplateDeclaration(params, declaration)

    def parse_class(self) -> ClassDeclaration:
        """Parse class/struct declaration."""
        is_struct = self.current_token.type == TokenType.STRUCT
        self.advance()

        name = self.expect(TokenType.IDENTIFIER).value

        # Base classes
        base_classes = []
        if self.match(TokenType.COLON):
            self.advance()
            while True:
                # Skip access specifiers
                if self.match(TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED):
                    self.advance()

                base_classes.append(self.expect(TokenType.IDENTIFIER).value)

                if not self.match(TokenType.COMMA):
                    break
                self.advance()

        self.expect(TokenType.LBRACE)

        members = []
        while not self.match(TokenType.RBRACE) and self.current_token.type != TokenType.EOF:
            # Access specifiers
            if self.match(TokenType.PUBLIC, TokenType.PRIVATE, TokenType.PROTECTED):
                access = self.advance().value
                self.expect(TokenType.COLON)
                members.append(AccessSpecifier(access))
                continue

            # Constructor
            if self.current_token.type == TokenType.IDENTIFIER and self.current_token.value == name:
                members.append(self.parse_constructor(name))
                continue

            # Destructor
            if self.match(TokenType.BITWISE_NOT):
                self.advance()
                if self.current_token.value == name:
                    members.append(self.parse_destructor(name))
                    continue

            # Regular member
            member = self.parse_function_or_variable()
            if member:
                members.append(member)

        self.expect(TokenType.RBRACE)
        self.match_and_consume(TokenType.SEMICOLON)

        return ClassDeclaration(name, base_classes, members, is_struct)

    def parse_constructor(self, class_name: str) -> ConstructorDeclaration:
        """Parse constructor."""
        self.expect(TokenType.IDENTIFIER)  # class name
        self.expect(TokenType.LPAREN)

        params = self.parse_parameter_list()
        self.expect(TokenType.RPAREN)

        # Initializer list
        initializers = []
        if self.match(TokenType.COLON):
            self.advance()
            while True:
                member_name = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.LPAREN)
                value = self.parse_expression()
                self.expect(TokenType.RPAREN)

                initializers.append(MemberInitializer(member_name, value))

                if not self.match(TokenType.COMMA):
                    break
                self.advance()

        body = None
        if self.match(TokenType.LBRACE):
            body = self.parse_compound_statement()
        else:
            self.expect(TokenType.SEMICOLON)

        return ConstructorDeclaration(class_name, params, initializers, body)

    def parse_destructor(self, class_name: str) -> DestructorDeclaration:
        """Parse destructor."""
        is_virtual = False
        self.expect(TokenType.IDENTIFIER)  # class name
        self.expect(TokenType.LPAREN)
        self.expect(TokenType.RPAREN)

        body = None
        if self.match(TokenType.LBRACE):
            body = self.parse_compound_statement()
        else:
            self.expect(TokenType.SEMICOLON)

        return DestructorDeclaration(class_name, body, is_virtual)

    def parse_enum(self) -> EnumDeclaration:
        """Parse enum declaration."""
        self.expect(TokenType.ENUM)

        # Optional 'class' or 'struct'
        self.match_and_consume(TokenType.CLASS, TokenType.STRUCT)

        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)

        enumerators = []
        while not self.match(TokenType.RBRACE):
            enum_name = self.expect(TokenType.IDENTIFIER).value
            value = None

            if self.match(TokenType.ASSIGN):
                self.advance()
                value = self.parse_expression()

            enumerators.append(Enumerator(enum_name, value))

            if not self.match(TokenType.RBRACE):
                self.expect(TokenType.COMMA)

        self.expect(TokenType.RBRACE)
        self.match_and_consume(TokenType.SEMICOLON)

        return EnumDeclaration(name, enumerators)

    def parse_typedef(self) -> TypedefDeclaration:
        """Parse typedef."""
        self.expect(TokenType.TYPEDEF)
        original_type = self.parse_type()
        new_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SEMICOLON)
        return TypedefDeclaration(original_type, new_name)

    def parse_function_or_variable(self) -> Optional[Declaration]:
        """Parse function or variable declaration."""
        # Storage specifiers
        is_static = self.match_and_consume(TokenType.STATIC) is not None
        is_extern = self.match_and_consume(TokenType.EXTERN) is not None
        is_inline = self.match_and_consume(TokenType.INLINE) is not None
        is_virtual = self.match_and_consume(TokenType.VIRTUAL) is not None
        is_constexpr = self.match_and_consume(TokenType.CONSTEXPR) is not None

        # Parse type
        return_type = self.parse_type()

        # Parse name
        if not self.match(TokenType.IDENTIFIER):
            return None
        name = self.advance().value

        # Function?
        if self.match(TokenType.LPAREN):
            self.advance()
            params = self.parse_parameter_list()
            self.expect(TokenType.RPAREN)

            # const, override, final
            is_const = self.match_and_consume(TokenType.CONST) is not None
            is_override = self.match_and_consume(TokenType.OVERRIDE) is not None
            is_final = self.match_and_consume(TokenType.FINAL) is not None

            # Function body or semicolon
            body = None
            if self.match(TokenType.LBRACE):
                body = self.parse_compound_statement()
            else:
                self.expect(TokenType.SEMICOLON)

            return FunctionDeclaration(
                return_type, name, params, body,
                is_inline, is_static, is_virtual, is_override, is_const
            )

        # Variable
        initializer = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initializer = self.parse_expression()

        self.expect(TokenType.SEMICOLON)

        return VariableDeclaration(
            return_type, name, initializer,
            is_static, is_extern, is_constexpr
        )

    def parse_parameter_list(self) -> List[Parameter]:
        """Parse function parameter list."""
        params = []

        if self.match(TokenType.RPAREN):
            return params

        while True:
            param_type = self.parse_type()
            param_name = ""

            if self.match(TokenType.IDENTIFIER):
                param_name = self.advance().value

            default_value = None
            if self.match(TokenType.ASSIGN):
                self.advance()
                default_value = self.parse_expression()

            params.append(Parameter(param_type, param_name, default_value))

            if not self.match(TokenType.COMMA):
                break
            self.advance()

        return params

    def parse_type(self) -> Type:
        """Parse type."""
        is_const = self.match_and_consume(TokenType.CONST) is not None
        is_volatile = self.match_and_consume(TokenType.VOLATILE) is not None
        is_signed = True

        # Signed/unsigned
        if self.match(TokenType.UNSIGNED):
            self.advance()
            is_signed = False
        elif self.match(TokenType.SIGNED):
            self.advance()

        # Base type
        base_type = None

        if self.match(TokenType.INT, TokenType.CHAR, TokenType.FLOAT,
                     TokenType.DOUBLE, TokenType.VOID, TokenType.BOOL,
                     TokenType.SHORT, TokenType.LONG):
            type_name = self.advance().value

            # Handle 'long long'
            if type_name == 'long' and self.match(TokenType.LONG):
                self.advance()
                type_name = 'long long'

            base_type = PrimitiveType(type_name, is_signed, is_const, is_volatile)

        elif self.match(TokenType.AUTO):
            self.advance()
            base_type = PrimitiveType('auto', True, is_const, is_volatile)

        elif self.match(TokenType.IDENTIFIER):
            type_name = self.advance().value
            base_type = UserDefinedType(type_name, is_const)

        else:
            self.error(f"Expected type, got {self.current_token.type.name}")

        # Pointers and references
        while self.match(TokenType.MULTIPLY, TokenType.BITWISE_AND):
            if self.current_token.type == TokenType.MULTIPLY:
                self.advance()
                ptr_const = self.match_and_consume(TokenType.CONST) is not None
                base_type = PointerType(base_type, ptr_const)
            else:  # Reference
                self.advance()
                base_type = ReferenceType(base_type)

        return base_type

    # Statement parsing
    def parse_statement(self) -> Statement:
        """Parse a statement."""
        # Compound statement
        if self.match(TokenType.LBRACE):
            return self.parse_compound_statement()

        # Return statement
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()

        # If statement
        if self.match(TokenType.IF):
            return self.parse_if_statement()

        # While statement
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()

        # Do-while statement
        if self.match(TokenType.DO):
            return self.parse_do_while_statement()

        # For statement
        if self.match(TokenType.FOR):
            return self.parse_for_statement()

        # Break statement
        if self.match(TokenType.BREAK):
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return BreakStatement()

        # Continue statement
        if self.match(TokenType.CONTINUE):
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return ContinueStatement()

        # Switch statement
        if self.match(TokenType.SWITCH):
            return self.parse_switch_statement()

        # Try statement
        if self.match(TokenType.TRY):
            return self.parse_try_statement()

        # Throw statement
        if self.match(TokenType.THROW):
            return self.parse_throw_statement()

        # Variable declaration or expression statement
        if self.is_type_start():
            decl = self.parse_function_or_variable()
            return ExpressionStatement(Identifier("declaration"))

        # Expression statement
        expr = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ExpressionStatement(expr)

    def is_type_start(self) -> bool:
        """Check if current token starts a type."""
        return self.match(
            TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE, TokenType.CHAR,
            TokenType.BOOL, TokenType.VOID, TokenType.SHORT, TokenType.LONG,
            TokenType.SIGNED, TokenType.UNSIGNED, TokenType.CONST,
            TokenType.VOLATILE, TokenType.AUTO
        )

    def parse_compound_statement(self) -> CompoundStatement:
        """Parse compound statement (block)."""
        self.expect(TokenType.LBRACE)
        statements = []

        while not self.match(TokenType.RBRACE) and self.current_token.type != TokenType.EOF:
            statements.append(self.parse_statement())

        self.expect(TokenType.RBRACE)
        return CompoundStatement(statements)

    def parse_return_statement(self) -> ReturnStatement:
        """Parse return statement."""
        self.expect(TokenType.RETURN)

        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.parse_expression()

        self.expect(TokenType.SEMICOLON)
        return ReturnStatement(value)

    def parse_if_statement(self) -> IfStatement:
        """Parse if statement."""
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)

        then_stmt = self.parse_statement()

        else_stmt = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_stmt = self.parse_statement()

        return IfStatement(condition, then_stmt, else_stmt)

    def parse_while_statement(self) -> WhileStatement:
        """Parse while statement."""
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        body = self.parse_statement()
        return WhileStatement(condition, body)

    def parse_do_while_statement(self) -> DoWhileStatement:
        """Parse do-while statement."""
        self.expect(TokenType.DO)
        body = self.parse_statement()
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return DoWhileStatement(body, condition)

    def parse_for_statement(self) -> ForStatement:
        """Parse for statement."""
        self.expect(TokenType.FOR)
        self.expect(TokenType.LPAREN)

        # Init
        init = None
        if not self.match(TokenType.SEMICOLON):
            init = self.parse_statement()
        else:
            self.advance()

        # Condition
        condition = None
        if not self.match(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.expect(TokenType.SEMICOLON)

        # Increment
        increment = None
        if not self.match(TokenType.RPAREN):
            increment = self.parse_expression()
        self.expect(TokenType.RPAREN)

        body = self.parse_statement()
        return ForStatement(init, condition, increment, body)

    def parse_switch_statement(self) -> SwitchStatement:
        """Parse switch statement."""
        self.expect(TokenType.SWITCH)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)

        cases = []
        while not self.match(TokenType.RBRACE):
            if self.match(TokenType.CASE):
                self.advance()
                value = self.parse_expression()
                self.expect(TokenType.COLON)

                statements = []
                while not self.match(TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE):
                    statements.append(self.parse_statement())

                cases.append(CaseStatement(value, statements))

            elif self.match(TokenType.DEFAULT):
                self.advance()
                self.expect(TokenType.COLON)

                statements = []
                while not self.match(TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE):
                    statements.append(self.parse_statement())

                cases.append(CaseStatement(None, statements))

        self.expect(TokenType.RBRACE)
        return SwitchStatement(condition, cases)

    def parse_try_statement(self) -> TryStatement:
        """Parse try-catch statement."""
        self.expect(TokenType.TRY)
        try_block = self.parse_compound_statement()

        catch_clauses = []
        while self.match(TokenType.CATCH):
            self.advance()
            self.expect(TokenType.LPAREN)

            exc_type = self.parse_type()
            exc_name = None
            if self.match(TokenType.IDENTIFIER):
                exc_name = self.advance().value

            self.expect(TokenType.RPAREN)
            body = self.parse_compound_statement()

            catch_clauses.append(CatchClause(exc_type, exc_name, body))

        return TryStatement(try_block, catch_clauses)

    def parse_throw_statement(self) -> ThrowStatement:
        """Parse throw statement."""
        self.expect(TokenType.THROW)

        expr = None
        if not self.match(TokenType.SEMICOLON):
            expr = self.parse_expression()

        self.expect(TokenType.SEMICOLON)
        return ThrowStatement(expr)

    # Expression parsing (precedence climbing)
    def parse_expression(self) -> Expression:
        """Parse expression."""
        return self.parse_assignment()

    def parse_assignment(self) -> Expression:
        """Parse assignment expression."""
        expr = self.parse_ternary()

        if self.match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN,
                     TokenType.MINUS_ASSIGN, TokenType.MULTIPLY_ASSIGN,
                     TokenType.DIVIDE_ASSIGN, TokenType.MODULO_ASSIGN):
            op = self.advance().value
            value = self.parse_assignment()
            return AssignmentExpression(expr, op, value)

        return expr

    def parse_ternary(self) -> Expression:
        """Parse ternary conditional expression."""
        expr = self.parse_logical_or()

        if self.match(TokenType.QUESTION):
            self.advance()
            true_expr = self.parse_expression()
            self.expect(TokenType.COLON)
            false_expr = self.parse_ternary()
            return TernaryExpression(expr, true_expr, false_expr)

        return expr

    def parse_logical_or(self) -> Expression:
        """Parse logical OR expression."""
        left = self.parse_logical_and()

        while self.match(TokenType.LOGICAL_OR):
            op = self.advance().value
            right = self.parse_logical_and()
            left = BinaryExpression(left, op, right)

        return left

    def parse_logical_and(self) -> Expression:
        """Parse logical AND expression."""
        left = self.parse_bitwise_or()

        while self.match(TokenType.LOGICAL_AND):
            op = self.advance().value
            right = self.parse_bitwise_or()
            left = BinaryExpression(left, op, right)

        return left

    def parse_bitwise_or(self) -> Expression:
        """Parse bitwise OR expression."""
        left = self.parse_bitwise_xor()

        while self.match(TokenType.BITWISE_OR):
            op = self.advance().value
            right = self.parse_bitwise_xor()
            left = BinaryExpression(left, op, right)

        return left

    def parse_bitwise_xor(self) -> Expression:
        """Parse bitwise XOR expression."""
        left = self.parse_bitwise_and()

        while self.match(TokenType.BITWISE_XOR):
            op = self.advance().value
            right = self.parse_bitwise_and()
            left = BinaryExpression(left, op, right)

        return left

    def parse_bitwise_and(self) -> Expression:
        """Parse bitwise AND expression."""
        left = self.parse_equality()

        while self.match(TokenType.BITWISE_AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryExpression(left, op, right)

        return left

    def parse_equality(self) -> Expression:
        """Parse equality expression."""
        left = self.parse_relational()

        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self.advance().value
            right = self.parse_relational()
            left = BinaryExpression(left, op, right)

        return left

    def parse_relational(self) -> Expression:
        """Parse relational expression."""
        left = self.parse_shift()

        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN,
                         TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
                         TokenType.SPACESHIP):
            op = self.advance().value
            right = self.parse_shift()
            left = BinaryExpression(left, op, right)

        return left

    def parse_shift(self) -> Expression:
        """Parse shift expression."""
        left = self.parse_additive()

        while self.match(TokenType.LEFT_SHIFT, TokenType.RIGHT_SHIFT):
            op = self.advance().value
            right = self.parse_additive()
            left = BinaryExpression(left, op, right)

        return left

    def parse_additive(self) -> Expression:
        """Parse additive expression."""
        left = self.parse_multiplicative()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinaryExpression(left, op, right)

        return left

    def parse_multiplicative(self) -> Expression:
        """Parse multiplicative expression."""
        left = self.parse_unary()

        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryExpression(left, op, right)

        return left

    def parse_unary(self) -> Expression:
        """Parse unary expression."""
        # Prefix unary operators
        if self.match(TokenType.INCREMENT, TokenType.DECREMENT,
                     TokenType.PLUS, TokenType.MINUS,
                     TokenType.LOGICAL_NOT, TokenType.BITWISE_NOT):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryExpression(op, operand, False)

        # Cast expressions
        if self.match(TokenType.STATIC_CAST, TokenType.DYNAMIC_CAST,
                     TokenType.CONST_CAST, TokenType.REINTERPRET_CAST):
            return self.parse_cast()

        # Sizeof
        if self.match(TokenType.SIZEOF):
            self.advance()
            self.expect(TokenType.LPAREN)
            operand = self.parse_type()
            self.expect(TokenType.RPAREN)
            return SizeofExpression(operand)

        # New
        if self.match(TokenType.NEW):
            return self.parse_new()

        # Delete
        if self.match(TokenType.DELETE):
            return self.parse_delete()

        return self.parse_postfix()

    def parse_cast(self) -> CastExpression:
        """Parse cast expression."""
        cast_type = self.advance().value.replace('_', '-')
        self.expect(TokenType.LESS_THAN)
        target_type = self.parse_type()
        self.expect(TokenType.GREATER_THAN)
        self.expect(TokenType.LPAREN)
        expr = self.parse_expression()
        self.expect(TokenType.RPAREN)
        return CastExpression(cast_type, target_type, expr)

    def parse_new(self) -> NewExpression:
        """Parse new expression."""
        self.expect(TokenType.NEW)

        is_array = False
        array_size = None

        # Check for array new
        if self.match(TokenType.LBRACKET):
            is_array = True
            self.advance()
            if not self.match(TokenType.RBRACKET):
                array_size = self.parse_expression()
            self.expect(TokenType.RBRACKET)

        allocated_type = self.parse_type()

        # Constructor arguments
        arguments = []
        if self.match(TokenType.LPAREN):
            self.advance()
            if not self.match(TokenType.RPAREN):
                arguments.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    arguments.append(self.parse_expression())
            self.expect(TokenType.RPAREN)

        return NewExpression(allocated_type, arguments, is_array, array_size)

    def parse_delete(self) -> DeleteExpression:
        """Parse delete expression."""
        self.expect(TokenType.DELETE)

        is_array = False
        if self.match(TokenType.LBRACKET):
            is_array = True
            self.advance()
            self.expect(TokenType.RBRACKET)

        expr = self.parse_unary()
        return DeleteExpression(expr, is_array)

    def parse_postfix(self) -> Expression:
        """Parse postfix expression."""
        expr = self.parse_primary()

        while True:
            # Postfix increment/decrement
            if self.match(TokenType.INCREMENT, TokenType.DECREMENT):
                op = self.advance().value
                expr = UnaryExpression(op, expr, True)

            # Function call
            elif self.match(TokenType.LPAREN):
                self.advance()
                args = []
                if not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                expr = CallExpression(expr, args)

            # Array access
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = ArrayAccessExpression(expr, index)

            # Member access
            elif self.match(TokenType.DOT):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                expr = MemberAccessExpression(expr, member, False)

            # Arrow member access
            elif self.match(TokenType.ARROW):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                expr = MemberAccessExpression(expr, member, True)

            else:
                break

        return expr

    def parse_primary(self) -> Expression:
        """Parse primary expression."""
        # Integer literal
        if self.match(TokenType.INTEGER):
            value = int(self.advance().value, 0)  # 0 handles hex, oct, bin
            return IntegerLiteral(value)

        # Float literal
        if self.match(TokenType.FLOAT_LITERAL):
            value = float(self.advance().value.rstrip('fFlL'))
            return FloatLiteral(value)

        # Character literal
        if self.match(TokenType.CHAR_LITERAL):
            value = self.advance().value
            return CharLiteral(value)

        # String literal
        if self.match(TokenType.STRING_LITERAL):
            value = self.advance().value
            return StringLiteral(value)

        # Boolean literals
        if self.match(TokenType.TRUE):
            self.advance()
            return BoolLiteral(True)

        if self.match(TokenType.FALSE):
            self.advance()
            return BoolLiteral(False)

        # Nullptr
        if self.match(TokenType.NULLPTR):
            self.advance()
            return NullptrLiteral()

        # This
        if self.match(TokenType.THIS):
            self.advance()
            return ThisExpression()

        # Identifier
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            return Identifier(name)

        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        self.error(f"Unexpected token in expression: {self.current_token.type.name}")