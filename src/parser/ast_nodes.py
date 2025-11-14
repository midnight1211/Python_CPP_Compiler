"""
Abstract Syntax Tree (AST) node definitions for C++.
Defines all AST node types used in the parser.
"""

from dataclasses import dataclass
from typing import List, Optional, Any
from abc import ABC, abstractmethod


# Base AST Node
class ASTNode(ABC):
    """Base class for all AST nodes."""

    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern."""
        pass


# Program and Translation Unit
@dataclass
class Program(ASTNode):
    """Root node representing the entire program."""
    declarations: List['Declaration']

    def accept(self, visitor):
        return visitor.visit_program(self)


# Types
@dataclass
class Type(ASTNode):
    """Base class for type nodes."""
    pass


@dataclass
class PrimitiveType(Type):
    """Primitive types: int, float, char, etc."""
    name: str  # 'int', 'float', 'double', 'char', 'bool', 'void'
    is_signed: bool = True
    is_const: bool = False
    is_volatile: bool = False

    def accept(self, visitor):
        return visitor.visit_primitive_type(self)


@dataclass
class PointerType(Type):
    """Pointer type."""
    base_type: Type
    is_const: bool = False

    def accept(self, visitor):
        return visitor.visit_pointer_type(self)


@dataclass
class ReferenceType(Type):
    """Reference type."""
    base_type: Type

    def accept(self, visitor):
        return visitor.visit_reference_type(self)


@dataclass
class ArrayType(Type):
    """Array type."""
    base_type: Type
    size: Optional['Expression'] = None

    def accept(self, visitor):
        return visitor.visit_array_type(self)


@dataclass
class UserDefinedType(Type):
    """User-defined types (class, struct, enum)."""
    name: str
    is_const: bool = False

    def accept(self, visitor):
        return visitor.visit_user_defined_type(self)


# Declarations
@dataclass
class Declaration(ASTNode):
    """Base class for declarations."""
    pass


@dataclass
class VariableDeclaration(Declaration):
    """Variable declaration."""
    var_type: Type
    name: str
    initializer: Optional['Expression'] = None
    is_static: bool = False
    is_extern: bool = False
    is_constexpr: bool = False

    def accept(self, visitor):
        return visitor.visit_variable_declaration(self)


@dataclass
class Parameter(ASTNode):
    """Function parameter."""
    param_type: Type
    name: str
    default_value: Optional['Expression'] = None

    def accept(self, visitor):
        return visitor.visit_parameter(self)


@dataclass
class FunctionDeclaration(Declaration):
    """Function declaration."""
    return_type: Type
    name: str
    parameters: List[Parameter]
    body: Optional['CompoundStatement'] = None
    is_inline: bool = False
    is_static: bool = False
    is_virtual: bool = False
    is_override: bool = False
    is_const: bool = False  # For const member functions

    def accept(self, visitor):
        return visitor.visit_function_declaration(self)


@dataclass
class ClassDeclaration(Declaration):
    """Class declaration."""
    name: str
    base_classes: List[str]
    members: List[Declaration]
    is_struct: bool = False

    def accept(self, visitor):
        return visitor.visit_class_declaration(self)


@dataclass
class AccessSpecifier(ASTNode):
    """Access specifier: public, private, protected."""
    access: str  # 'public', 'private', 'protected'

    def accept(self, visitor):
        return visitor.visit_access_specifier(self)


@dataclass
class ConstructorDeclaration(Declaration):
    """Constructor declaration."""
    class_name: str
    parameters: List[Parameter]
    initializer_list: List['MemberInitializer']
    body: Optional['CompoundStatement'] = None

    def accept(self, visitor):
        return visitor.visit_constructor_declaration(self)


@dataclass
class DestructorDeclaration(Declaration):
    """Destructor declaration."""
    class_name: str
    body: Optional['CompoundStatement'] = None
    is_virtual: bool = False

    def accept(self, visitor):
        return visitor.visit_destructor_declaration(self)


@dataclass
class MemberInitializer(ASTNode):
    """Member initializer in constructor."""
    member_name: str
    value: 'Expression'

    def accept(self, visitor):
        return visitor.visit_member_initializer(self)


@dataclass
class NamespaceDeclaration(Declaration):
    """Namespace declaration."""
    name: str
    declarations: List[Declaration]

    def accept(self, visitor):
        return visitor.visit_namespace_declaration(self)


@dataclass
class UsingDeclaration(Declaration):
    """Using declaration."""
    namespace_name: str

    def accept(self, visitor):
        return visitor.visit_using_declaration(self)


@dataclass
class TypedefDeclaration(Declaration):
    """Typedef declaration."""
    original_type: Type
    new_name: str

    def accept(self, visitor):
        return visitor.visit_typedef_declaration(self)


@dataclass
class EnumDeclaration(Declaration):
    """Enum declaration."""
    name: str
    enumerators: List['Enumerator']

    def accept(self, visitor):
        return visitor.visit_enum_declaration(self)


@dataclass
class Enumerator(ASTNode):
    """Single enumerator in enum."""
    name: str
    value: Optional['Expression'] = None

    def accept(self, visitor):
        return visitor.visit_enumerator(self)


@dataclass
class TemplateDeclaration(Declaration):
    """Template declaration."""
    template_parameters: List['TemplateParameter']
    declaration: Declaration

    def accept(self, visitor):
        return visitor.visit_template_declaration(self)


@dataclass
class TemplateParameter(ASTNode):
    """Template parameter."""
    kind: str  # 'typename' or 'class'
    name: str
    default_type: Optional[Type] = None

    def accept(self, visitor):
        return visitor.visit_template_parameter(self)


# Statements
@dataclass
class Statement(ASTNode):
    """Base class for statements."""
    pass


@dataclass
class CompoundStatement(Statement):
    """Compound statement (block)."""
    statements: List[Statement]

    def accept(self, visitor):
        return visitor.visit_compound_statement(self)


@dataclass
class ExpressionStatement(Statement):
    """Expression statement."""
    expression: 'Expression'

    def accept(self, visitor):
        return visitor.visit_expression_statement(self)


@dataclass
class ReturnStatement(Statement):
    """Return statement."""
    value: Optional['Expression'] = None

    def accept(self, visitor):
        return visitor.visit_return_statement(self)


@dataclass
class IfStatement(Statement):
    """If statement."""
    condition: 'Expression'
    then_statement: Statement
    else_statement: Optional[Statement] = None

    def accept(self, visitor):
        return visitor.visit_if_statement(self)


@dataclass
class WhileStatement(Statement):
    """While loop."""
    condition: 'Expression'
    body: Statement

    def accept(self, visitor):
        return visitor.visit_while_statement(self)


@dataclass
class DoWhileStatement(Statement):
    """Do-while loop."""
    body: Statement
    condition: 'Expression'

    def accept(self, visitor):
        return visitor.visit_do_while_statement(self)


@dataclass
class ForStatement(Statement):
    """For loop."""
    init: Optional[Statement]
    condition: Optional['Expression']
    increment: Optional['Expression']
    body: Statement

    def accept(self, visitor):
        return visitor.visit_for_statement(self)


@dataclass
class BreakStatement(Statement):
    """Break statement."""

    def accept(self, visitor):
        return visitor.visit_break_statement(self)


@dataclass
class ContinueStatement(Statement):
    """Continue statement."""

    def accept(self, visitor):
        return visitor.visit_continue_statement(self)


@dataclass
class SwitchStatement(Statement):
    """Switch statement."""
    condition: 'Expression'
    cases: List['CaseStatement']

    def accept(self, visitor):
        return visitor.visit_switch_statement(self)


@dataclass
class CaseStatement(Statement):
    """Case statement in switch."""
    value: Optional['Expression']  # None for default case
    statements: List[Statement]

    def accept(self, visitor):
        return visitor.visit_case_statement(self)


@dataclass
class TryStatement(Statement):
    """Try-catch statement."""
    try_block: CompoundStatement
    catch_clauses: List['CatchClause']

    def accept(self, visitor):
        return visitor.visit_try_statement(self)


@dataclass
class CatchClause(ASTNode):
    """Catch clause."""
    exception_type: Type
    exception_name: Optional[str]
    body: CompoundStatement

    def accept(self, visitor):
        return visitor.visit_catch_clause(self)


@dataclass
class ThrowStatement(Statement):
    """Throw statement."""
    expression: Optional['Expression'] = None

    def accept(self, visitor):
        return visitor.visit_throw_statement(self)


# Expressions
@dataclass
class Expression(ASTNode):
    """Base class for expressions."""
    pass


@dataclass
class IntegerLiteral(Expression):
    """Integer literal."""
    value: int

    def accept(self, visitor):
        return visitor.visit_integer_literal(self)


@dataclass
class FloatLiteral(Expression):
    """Floating-point literal."""
    value: float

    def accept(self, visitor):
        return visitor.visit_float_literal(self)


@dataclass
class CharLiteral(Expression):
    """Character literal."""
    value: str

    def accept(self, visitor):
        return visitor.visit_char_literal(self)


@dataclass
class StringLiteral(Expression):
    """String literal."""
    value: str

    def accept(self, visitor):
        return visitor.visit_string_literal(self)


@dataclass
class BoolLiteral(Expression):
    """Boolean literal."""
    value: bool

    def accept(self, visitor):
        return visitor.visit_bool_literal(self)


@dataclass
class NullptrLiteral(Expression):
    """Nullptr literal."""

    def accept(self, visitor):
        return visitor.visit_nullptr_literal(self)


@dataclass
class Identifier(Expression):
    """Identifier."""
    name: str

    def accept(self, visitor):
        return visitor.visit_identifier(self)


@dataclass
class BinaryExpression(Expression):
    """Binary expression."""
    left: Expression
    operator: str
    right: Expression

    def accept(self, visitor):
        return visitor.visit_binary_expression(self)


@dataclass
class UnaryExpression(Expression):
    """Unary expression."""
    operator: str
    operand: Expression
    is_postfix: bool = False

    def accept(self, visitor):
        return visitor.visit_unary_expression(self)


@dataclass
class AssignmentExpression(Expression):
    """Assignment expression."""
    target: Expression
    operator: str  # '=', '+=', '-=', etc.
    value: Expression

    def accept(self, visitor):
        return visitor.visit_assignment_expression(self)


@dataclass
class CallExpression(Expression):
    """Function call expression."""
    function: Expression
    arguments: List[Expression]

    def accept(self, visitor):
        return visitor.visit_call_expression(self)


@dataclass
class MemberAccessExpression(Expression):
    """Member access expression (. or ->)."""
    object: Expression
    member: str
    is_arrow: bool = False  # True for ->, False for .

    def accept(self, visitor):
        return visitor.visit_member_access_expression(self)


@dataclass
class ArrayAccessExpression(Expression):
    """Array access expression."""
    array: Expression
    index: Expression

    def accept(self, visitor):
        return visitor.visit_array_access_expression(self)


@dataclass
class TernaryExpression(Expression):
    """Ternary conditional expression."""
    condition: Expression
    true_expr: Expression
    false_expr: Expression

    def accept(self, visitor):
        return visitor.visit_ternary_expression(self)


@dataclass
class CastExpression(Expression):
    """Cast expression."""
    cast_type: str  # 'static_cast', 'dynamic_cast', 'const_cast', 'reinterpret_cast', or 'c_style'
    target_type: Type
    expression: Expression

    def accept(self, visitor):
        return visitor.visit_cast_expression(self)


@dataclass
class NewExpression(Expression):
    """New expression."""
    allocated_type: Type
    arguments: List[Expression]
    is_array: bool = False
    array_size: Optional[Expression] = None

    def accept(self, visitor):
        return visitor.visit_new_expression(self)


@dataclass
class DeleteExpression(Expression):
    """Delete expression."""
    expression: Expression
    is_array: bool = False

    def accept(self, visitor):
        return visitor.visit_delete_expression(self)


@dataclass
class SizeofExpression(Expression):
    """Sizeof expression."""
    operand: Any  # Can be Type or Expression

    def accept(self, visitor):
        return visitor.visit_sizeof_expression(self)


@dataclass
class ThisExpression(Expression):
    """This pointer expression."""

    def accept(self, visitor):
        return visitor.visit_this_expression(self)


@dataclass
class LambdaExpression(Expression):
    """Lambda expression."""
    captures: List[str]
    parameters: List[Parameter]
    return_type: Optional[Type]
    body: CompoundStatement

    def accept(self, visitor):
        return visitor.visit_lambda_expression(self)