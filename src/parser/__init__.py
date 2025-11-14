"""
Parser package for the C++ compiler.

This package contains the syntax analysis components:
 - Parser: The main recursive descent parser
 - AST Nodes: All Abstract Syntax Tree node definitions

Example usageL
    from src.lexer import Lexer
    from src.parser import Parser

    source_code = '''
    int main() {
        int X = 5;
        return X * 2;
    }
    '''

    # Tokenize
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    # Parse
    parser = Parser(tokens)
    ast = parser.parse()

    # Access AST
    print(f"Program has {len(ast.declarations)} declarations")
"""

from .parser import Parser, ParserError
from .ast_nodes import *

__all__ = [
    'Parser',
    'ParserError',
    # Base nodes
    'ASTNode',
    'Program',
    # Types
    'Type',
    'PrimitiveType',
    'PointerType',
    'ReferenceType',
    'ArrayType',
    'UserDefinedType',
    # Declarations
'Declaration',
    'VariableDeclaration',
    'FunctionDeclaration',
    'Parameter',
    'ClassDeclaration',
    'AccessSpecifier',
    'ConstructorDeclaration',
    'DestructorDeclaration',
    'MemberInitializer',
    'NamespaceDeclaration',
    'UsingDeclaration',
    'TypedefDeclaration',
    'EnumDeclaration',
    'Enumerator',
    'TemplateDeclaration',
    'TemplateParameter',
    # Statements
    'Statement',
    'CompoundStatement',
    'ExpressionStatement',
    'ReturnStatement',
    'IfStatement',
    'WhileStatement',
    'DoWhileStatement',
    'ForStatement',
    'BreakStatement',
    'ContinueStatement',
    'SwitchStatement',
    'CaseStatement',
    'TryStatement',
    'CatchClause',
    'ThrowStatement',
    # Expressions
    'Expression',
    'IntegerLiteral',
    'FloatLiteral',
    'CharLiteral',
    'StringLiteral',
    'BoolLiteral',
    'NullptrLiteral',
    'Identifier',
    'BinaryExpression',
    'UnaryExpression',
    'AssignmentExpression',
    'CallExpression',
    'MemberAccessExpression',
    'ArrayAccessExpression',
    'TernaryExpression',
    'CastExpression',
    'NewExpression',
    'DeleteExpression',
    'SizeofExpression',
    'ThisExpression',
    'LambdaExpression',
]

__version__ = '1.0.0'
__author__ = 'David Vuksanovich'
__description__ = 'Syntax analyzer for C++ compiler'