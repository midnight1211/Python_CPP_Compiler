"""
Semantic Analyzer for the C++ compiler.
Performs semantic analysis on the AST including:
- Symbol table construction
- Type checking
- Scope management
- Name resolution
"""

from typing import Optional, List, Any
import sys

sys.path.append('../..')

from src.parser.ast_nodes import *
from .symbol_table import SymbolTable, SymbolKind, TypeRegistry
from .type_checker import TypeChecker, TypeCheckError


class SemanticError(Exception):
    """Exception raised for semantic analysis errors."""

    def __init__(self, message: str, node: Optional[ASTNode] = None):
        self.message = message
        self.node = node
        super().__init__(f"Semantic error: {message}")


class SemanticAnalyzer:
    """
    Semantic analyzer using the Visitor pattern.

    Traverses the AST and performs:
    1. Symbol table construction
    2. Type checking
    3. Scope validation
    4. Name resolution
    5. Semantic constraint checking
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.type_registry = TypeRegistry()
        self.type_checker = TypeChecker(self.type_registry)
        self.errors: List[str] = []
        self.in_loop = False  # Track if we're inside a loop
        self.in_switch = False  # Track if we're inside a switch

    def analyze(self, program: Program) -> bool:
        """
        Analyze a program.

        Args:
            program: Program AST node

        Returns:
            True if analysis succeeded, False if errors occurred
        """
        try:
            self.visit_program(program)
            return len(self.errors) == 0
        except SemanticError as e:
            self.errors.append(str(e))
            return False

    def error(self, message: str, node: Optional[ASTNode] = None) -> None:
        """Record a semantic error."""
        error = SemanticError(message, node)
        self.errors.append(str(error))

    # Visitor methods for Program
    def visit_program(self, node: Program) -> None:
        """Visit program node."""
        for declaration in node.declarations:
            declaration.accept(self)

    # Visitor methods for Declarations
    def visit_variable_declaration(self, node: VariableDeclaration) -> None:
        """Visit variable declaration."""
        try:
            # Define the variable in symbol table
            self.symbol_table.define(
                name=node.name,
                kind=SymbolKind.VARIABLE,
                symbol_type=node.var_type,
                is_static=node.is_static,
                is_extern=node.is_extern,
                is_constexpr=node.is_constexpr
            )

            # Type check initializer if present
            if node.initializer:
                init_type = self.type_checker.infer_type(node.initializer)
                if not self.type_checker.check_type_compatibility(init_type, node.var_type):
                    self.error(
                        f"Cannot initialize variable '{node.name}' of type "
                        f"{self.type_to_string(node.var_type)} with value of type "
                        f"{self.type_to_string(init_type)}"
                    )

        except Exception as e:
            self.error(f"Variable declaration error: {e}")

    def visit_function_declaration(self, node: FunctionDeclaration) -> None:
        """Visit function declaration."""
        try:
            # Get parameter types
            param_types = [param.param_type for param in node.parameters]

            # Define the function
            self.symbol_table.define_function(
                name=node.name,
                return_type=node.return_type,
                parameter_types=param_types,
                is_inline=node.is_inline,
                is_static=node.is_static,
                is_virtual=node.is_virtual,
                is_override=node.is_override,
                is_const=node.is_const
            )

            # Process function body if present
            if node.body:
                self.symbol_table.enter_function(node.name)

                # Set current function return type for return statement checking
                old_return_type = self.type_checker.current_function_return_type
                self.type_checker.current_function_return_type = node.return_type

                # Add parameters to function scope
                for param in node.parameters:
                    self.visit_parameter(param)

                # Visit body
                node.body.accept(self)

                # Restore return type
                self.type_checker.current_function_return_type = old_return_type

                self.symbol_table.exit_function()

        except Exception as e:
            self.error(f"Function declaration error: {e}")

    def visit_parameter(self, node: Parameter) -> None:
        """Visit parameter."""
        try:
            self.symbol_table.define(
                name=node.name,
                kind=SymbolKind.PARAMETER,
                symbol_type=node.param_type
            )
        except Exception as e:
            self.error(f"Parameter error: {e}")

    def visit_class_declaration(self, node: ClassDeclaration) -> None:
        """Visit class declaration."""
        try:
            # Register the class type
            self.type_registry.register_class(
                name=node.name,
                type_node=node,
                base_classes=node.base_classes
            )

            # Define class symbol
            self.symbol_table.define(
                name=node.name,
                kind=SymbolKind.CLASS,
                symbol_type=UserDefinedType(node.name),
                is_struct=node.is_struct
            )

            # Enter class scope
            self.symbol_table.enter_class(node.name)

            current_access = 'private' if not node.is_struct else 'public'

            # Process members
            for member in node.members:
                if isinstance(member, AccessSpecifier):
                    current_access = member.access
                else:
                    # Add member to type registry
                    if isinstance(member, (VariableDeclaration, FunctionDeclaration)):
                        member.accept(self)

                        # Track in type registry
                        symbol = self.symbol_table.lookup(member.name)
                        if symbol:
                            self.type_registry.add_class_member(node.name, symbol)
                    else:
                        member.accept(self)

            # Exit class scope
            self.symbol_table.exit_class()

        except Exception as e:
            self.error(f"Class declaration error: {e}")

    def visit_constructor_declaration(self, node: ConstructorDeclaration) -> None:
        """Visit constructor declaration."""
        try:
            self.symbol_table.enter_function(f"{node.class_name}::constructor")

            # Add parameters
            for param in node.parameters:
                self.visit_parameter(param)

            # Check initializer list
            for init in node.initializer_list:
                init.accept(self)

            # Visit body
            if node.body:
                node.body.accept(self)

            self.symbol_table.exit_function()

        except Exception as e:
            self.error(f"Constructor error: {e}")

    def visit_destructor_declaration(self, node: DestructorDeclaration) -> None:
        """Visit destructor declaration."""
        try:
            self.symbol_table.enter_function(f"{node.class_name}::destructor")

            if node.body:
                node.body.accept(self)

            self.symbol_table.exit_function()

        except Exception as e:
            self.error(f"Destructor error: {e}")

    def visit_namespace_declaration(self, node: NamespaceDeclaration) -> None:
        """Visit namespace declaration."""
        try:
            self.symbol_table.enter_namespace(node.name)

            for declaration in node.declarations:
                declaration.accept(self)

            self.symbol_table.exit_namespace()

        except Exception as e:
            self.error(f"Namespace error: {e}")

    def visit_enum_declaration(self, node: EnumDeclaration) -> None:
        """Visit enum declaration."""
        try:
            # Register enum type
            self.type_registry.register_type(node.name, node)

            # Define enum symbol
            self.symbol_table.define(
                name=node.name,
                kind=SymbolKind.ENUM,
                symbol_type=UserDefinedType(node.name)
            )

            # Process enumerators
            for enumerator in node.enumerators:
                enumerator.accept(self)

        except Exception as e:
            self.error(f"Enum declaration error: {e}")

    def visit_enumerator(self, node: Enumerator) -> None:
        """Visit enumerator."""
        try:
            self.symbol_table.define(
                name=node.name,
                kind=SymbolKind.VARIABLE,
                symbol_type=PrimitiveType('int'),
                is_const=True
            )
        except Exception as e:
            self.error(f"Enumerator error: {e}")

    def visit_template_declaration(self, node: TemplateDeclaration) -> None:
        """Visit template declaration."""
        try:
            # For simplicity, just visit the declaration
            # Full template support would require template instantiation
            node.declaration.accept(self)
        except Exception as e:
            self.error(f"Template error: {e}")

    # Visitor methods for Statements
    def visit_compound_statement(self, node: CompoundStatement) -> None:
        """Visit compound statement."""
        self.symbol_table.enter_scope("block")

        for statement in node.statements:
            statement.accept(self)

        self.symbol_table.exit_scope()

    def visit_expression_statement(self, node: ExpressionStatement) -> None:
        """Visit expression statement."""
        node.expression.accept(self)

    def visit_return_statement(self, node: ReturnStatement) -> None:
        """Visit return statement."""
        try:
            if node.value:
                return_type = self.type_checker.infer_type(node.value)
                self.type_checker.check_return_type(return_type)
            else:
                self.type_checker.check_return_type(None)
        except TypeCheckError as e:
            self.error(str(e))

    def visit_if_statement(self, node: IfStatement) -> None:
        """Visit if statement."""
        # Check condition
        node.condition.accept(self)

        # Visit branches
        node.then_statement.accept(self)
        if node.else_statement:
            node.else_statement.accept(self)

    def visit_while_statement(self, node: WhileStatement) -> None:
        """Visit while statement."""
        old_in_loop = self.in_loop
        self.in_loop = True

        node.condition.accept(self)
        node.body.accept(self)

        self.in_loop = old_in_loop

    def visit_do_while_statement(self, node: DoWhileStatement) -> None:
        """Visit do-while statement."""
        old_in_loop = self.in_loop
        self.in_loop = True

        node.body.accept(self)
        node.condition.accept(self)

        self.in_loop = old_in_loop

    def visit_for_statement(self, node: ForStatement) -> None:
        """Visit for statement."""
        old_in_loop = self.in_loop
        self.in_loop = True

        self.symbol_table.enter_scope("for")

        if node.init:
            node.init.accept(self)

        if node.condition:
            node.condition.accept(self)

        if node.increment:
            node.increment.accept(self)

        node.body.accept(self)

        self.symbol_table.exit_scope()

        self.in_loop = old_in_loop

    def visit_break_statement(self, node: BreakStatement) -> None:
        """Visit break statement."""
        if not self.in_loop and not self.in_switch:
            self.error("'break' statement not in loop or switch")

    def visit_continue_statement(self, node: ContinueStatement) -> None:
        """Visit continue statement."""
        if not self.in_loop:
            self.error("'continue' statement not in loop")

    def visit_switch_statement(self, node: SwitchStatement) -> None:
        """Visit switch statement."""
        old_in_switch = self.in_switch
        self.in_switch = True

        node.condition.accept(self)

        for case in node.cases:
            case.accept(self)

        self.in_switch = old_in_switch

    def visit_case_statement(self, node: CaseStatement) -> None:
        """Visit case statement."""
        if node.value:
            node.value.accept(self)

        for statement in node.statements:
            statement.accept(self)

    def visit_try_statement(self, node: TryStatement) -> None:
        """Visit try statement."""
        node.try_block.accept(self)

        for catch_clause in node.catch_clauses:
            catch_clause.accept(self)

    def visit_catch_clause(self, node: CatchClause) -> None:
        """Visit catch clause."""
        self.symbol_table.enter_scope("catch")

        # Add exception variable if named
        if node.exception_name:
            self.symbol_table.define(
                name=node.exception_name,
                kind=SymbolKind.VARIABLE,
                symbol_type=node.exception_type
            )

        node.body.accept(self)

        self.symbol_table.exit_scope()

    def visit_throw_statement(self, node: ThrowStatement) -> None:
        """Visit throw statement."""
        if node.expression:
            node.expression.accept(self)

    # Visitor methods for Expressions
    def visit_identifier(self, node: Identifier) -> Type:
        """Visit identifier."""
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.error(f"Undefined identifier: '{node.name}'")
            return PrimitiveType('int')  # Return dummy type

        return symbol.symbol_type

    def visit_binary_expression(self, node: BinaryExpression) -> Type:
        """Visit binary expression."""
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)

        try:
            result_type = self.type_checker.get_binary_operation_type(
                left_type, node.operator, right_type
            )
            return result_type
        except TypeCheckError as e:
            self.error(str(e))
            return PrimitiveType('int')  # Return dummy type

    def visit_unary_expression(self, node: UnaryExpression) -> Type:
        """Visit unary expression."""
        operand_type = node.operand.accept(self)

        try:
            result_type = self.type_checker.get_unary_operation_type(
                node.operator, operand_type
            )
            return result_type
        except TypeCheckError as e:
            self.error(str(e))
            return PrimitiveType('int')  # Return dummy type

    def visit_call_expression(self, node: CallExpression) -> Type:
        """Visit call expression."""
        # Get function type
        func_type = node.function.accept(self)

        # Get argument types
        arg_types = [arg.accept(self) for arg in node.arguments]

        # For full implementation, would check against function signature
        return func_type

    # Visitor methods for Literals
    def visit_integer_literal(self, node: IntegerLiteral) -> Type:
        """Visit integer literal."""
        return PrimitiveType('int')

    def visit_float_literal(self, node: FloatLiteral) -> Type:
        """Visit float literal."""
        return PrimitiveType('double')

    def visit_string_literal(self, node: StringLiteral) -> Type:
        """Visit string literal."""
        return PointerType(PrimitiveType('char', is_const=True))

    def visit_bool_literal(self, node: BoolLiteral) -> Type:
        """Visit bool literal."""
        return PrimitiveType('bool')

    # Helper methods
    def type_to_string(self, type_node: Type) -> str:
        """Convert type to string representation."""
        if isinstance(type_node, PrimitiveType):
            qualifiers = []
            if type_node.is_const:
                qualifiers.append('const')
            if type_node.is_volatile:
                qualifiers.append('volatile')
            if not type_node.is_signed and type_node.name in ['int', 'char']:
                qualifiers.append('unsigned')

            return ' '.join(qualifiers + [type_node.name])

        if isinstance(type_node, PointerType):
            return f"{self.type_to_string(type_node.base_type)}*"

        if isinstance(type_node, ReferenceType):
            return f"{self.type_to_string(type_node.base_type)}&"

        if isinstance(type_node, UserDefinedType):
            return type_node.name

        return "unknown"

    def dump_symbol_table(self) -> None:
        """Dump the symbol table for debugging."""
        self.symbol_table.dump()
        self.type_registry.dump()

    def print_errors(self) -> None:
        """Print all semantic errors."""
        if self.errors:
            print("\n" + "=" * 80)
            print("SEMANTIC ERRORS")
            print("=" * 80)
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
        else:
            print("\n✓ No semantic errors")