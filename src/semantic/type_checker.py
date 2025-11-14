"""
Type Checker for the C++ compiler.
Performs type checking and type inference on the AST.
"""

from typing import Optional, Any, List
import sys
sys.path.append('../..')

from src.parser.ast_nodes import *
from .symbol_table import TypeRegistry


class TypeCheckError(Exception):
    """Exception raised for type checking errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Type error: {message}")


class TypeChecker:
    """
    Type checker that validates type correctness in the AST.

    Checks:
    - Type compatibility in assignments
    - Function call argument types
    - Return type consistency
    - Operator type correctness
    - Array bounds (where possible)
    """

    def __init__(self, type_registry: TypeRegistry):
        self.type_registry = type_registry
        self.current_function_return_type: Optional[Type] = None

    def check_type_compatibility(self, source: Type, target: Type) -> bool:
        """
        Check if source type is compatible with target type.

        Args:
            source: Source type
            target: Target type

        Returns:
            True if compatible, False otherwise
        """
        # Same type
        if self.types_equal(source, target):
            return True

        # Pointer/reference compatibility
        if isinstance(target, PointerType) and isinstance(source, PointerType):
            return self.check_type_compatibility(source.base_type, target.base_type)

        # Numeric conversions
        if isinstance(source, PrimitiveType) and isinstance(target, PrimitiveType):
            return self.check_numeric_conversion(source, target)

        # Class hierarchy (inheritance)
        if isinstance(source, UserDefinedType) and isinstance(target, UserDefinedType):
            return self.check_class_compatibility(source.name, target.name)

        # Null pointer to pointer
        if isinstance(target, PointerType) and isinstance(source, PrimitiveType):
            if source.name == 'nullptr_t':
                return True

        return False

    def types_equal(self, type1: Type, type2: Type) -> bool:
        """Check if two types are exactly equal."""
        if type(type1) != type(type2):
            return False

        if isinstance(type1, PrimitiveType):
            return (type1.name == type2.name and
                   type1.is_signed == type2.is_signed)

        if isinstance(type1, PointerType):
            return self.types_equal(type1.base_type, type2.base_type)

        if isinstance(type1, ReferenceType):
            return self.types_equal(type1.base_type, type2.base_type)

        if isinstance(type1, ArrayType):
            return self.types_equal(type1.base_type, type2.base_type)

        if isinstance(type1, UserDefinedType):
            return type1.name == type2.name

        return False

    def check_numeric_conversion(self, source: PrimitiveType,
                                 target: PrimitiveType) -> bool:
        """Check if numeric conversion is valid."""
        numeric_types = {'int', 'float', 'double', 'char', 'short', 'long', 'long long'}

        if source.name not in numeric_types or target.name not in numeric_types:
            return False

        # All numeric types can be converted (with potential warnings)
        return True

    def check_class_compatibility(self, source_class: str,
                                  target_class: str) -> bool:
        """Check if source class is compatible with target class (inheritance)."""
        if source_class == target_class:
            return True

        # Check if source is derived from target
        return self.type_registry.is_derived_from(source_class, target_class)

    def get_binary_operation_type(self, left: Type, operator: str,
                                  right: Type) -> Type:
        """
        Determine the result type of a binary operation.

        Args:
            left: Left operand type
            operator: Operator string
            right: Right operand type

        Returns:
            Result type

        Raises:
            TypeCheckError: If operation is invalid
        """
        # Comparison operators return bool
        if operator in ['==', '!=', '<', '>', '<=', '>=', '<=>']:
            if not self.check_type_compatibility(left, right) and \
               not self.check_type_compatibility(right, left):
                raise TypeCheckError(
                    f"Cannot compare incompatible types in '{operator}' operation"
                )
            return PrimitiveType('bool')

        # Logical operators
        if operator in ['&&', '||']:
            if not self.is_boolean_compatible(left) or \
               not self.is_boolean_compatible(right):
                raise TypeCheckError(
                    f"Logical operator '{operator}' requires boolean operands"
                )
            return PrimitiveType('bool')

        # Arithmetic operators
        if operator in ['+', '-', '*', '/', '%']:
            if not isinstance(left, PrimitiveType) or \
               not isinstance(right, PrimitiveType):
                raise TypeCheckError(
                    f"Arithmetic operator '{operator}' requires numeric operands"
                )

            # Return the "wider" type
            return self.get_wider_type(left, right)

        # Bitwise operators
        if operator in ['&', '|', '^', '<<', '>>']:
            if not self.is_integral_type(left) or not self.is_integral_type(right):
                raise TypeCheckError(
                    f"Bitwise operator '{operator}' requires integral operands"
                )
            return self.get_wider_type(left, right)

        raise TypeCheckError(f"Unknown binary operator: {operator}")

    def get_unary_operation_type(self, operator: str, operand: Type) -> Type:
        """
        Determine the result type of a unary operation.

        Args:
            operator: Operator string
            operand: Operand type

        Returns:
            Result type

        Raises:
            TypeCheckError: If operation is invalid
        """
        # Logical NOT
        if operator == '!':
            if not self.is_boolean_compatible(operand):
                raise TypeCheckError("Logical NOT requires boolean operand")
            return PrimitiveType('bool')

        # Bitwise NOT
        if operator == '~':
            if not self.is_integral_type(operand):
                raise TypeCheckError("Bitwise NOT requires integral operand")
            return operand

        # Arithmetic unary
        if operator in ['+', '-']:
            if not isinstance(operand, PrimitiveType):
                raise TypeCheckError(
                    f"Unary '{operator}' requires numeric operand"
                )
            return operand

        # Increment/decrement
        if operator in ['++', '--']:
            if not isinstance(operand, PrimitiveType) and \
               not isinstance(operand, PointerType):
                raise TypeCheckError(
                    f"'{operator}' requires numeric or pointer operand"
                )
            return operand

        # Dereference
        if operator == '*':
            if not isinstance(operand, PointerType):
                raise TypeCheckError("Dereference requires pointer type")
            return operand.base_type

        # Address-of
        if operator == '&':
            return PointerType(operand)

        raise TypeCheckError(f"Unknown unary operator: {operator}")

    def is_boolean_compatible(self, type_node: Type) -> bool:
        """Check if a type can be used in boolean context."""
        if isinstance(type_node, PrimitiveType):
            return True  # All primitives can be used as boolean
        if isinstance(type_node, PointerType):
            return True  # Pointers can be used as boolean
        return False

    def is_integral_type(self, type_node: Type) -> bool:
        """Check if a type is an integral type."""
        if isinstance(type_node, PrimitiveType):
            return type_node.name in ['int', 'char', 'short', 'long', 'long long', 'bool']
        return False

    def is_numeric_type(self, type_node: Type) -> bool:
        """Check if a type is numeric."""
        if isinstance(type_node, PrimitiveType):
            return type_node.name in ['int', 'char', 'short', 'long', 'long long',
                                     'float', 'double', 'bool']
        return False

    def get_wider_type(self, type1: PrimitiveType, type2: PrimitiveType) -> PrimitiveType:
        """Get the wider of two numeric types for type promotion."""
        type_width = {
            'bool': 0,
            'char': 1,
            'short': 2,
            'int': 3,
            'long': 4,
            'long long': 5,
            'float': 6,
            'double': 7,
        }

        width1 = type_width.get(type1.name, 3)
        width2 = type_width.get(type2.name, 3)

        return type1 if width1 >= width2 else type2

    def check_function_call(self, function_type: Type, arg_types: List[Type],
                           param_types: List[Type]) -> Type:
        """
        Check if function call is valid.

        Args:
            function_type: Return type of the function
            arg_types: Argument types
            param_types: Parameter types

        Returns:
            Return type

        Raises:
            TypeCheckError: If call is invalid
        """
        if len(arg_types) != len(param_types):
            raise TypeCheckError(
                f"Function call: expected {len(param_types)} arguments, "
                f"got {len(arg_types)}"
            )

        for i, (arg_type, param_type) in enumerate(zip(arg_types, param_types)):
            if not self.check_type_compatibility(arg_type, param_type):
                raise TypeCheckError(
                    f"Function call: argument {i+1} type mismatch. "
                    f"Expected compatible with parameter type"
                )

        return function_type

    def check_array_access(self, array_type: Type, index_type: Type) -> Type:
        """
        Check array access operation.

        Args:
            array_type: Type of the array
            index_type: Type of the index

        Returns:
            Element type

        Raises:
            TypeCheckError: If access is invalid
        """
        # Check if array_type is actually an array or pointer
        if isinstance(array_type, ArrayType):
            base_type = array_type.base_type
        elif isinstance(array_type, PointerType):
            base_type = array_type.base_type
        else:
            raise TypeCheckError("Array access requires array or pointer type")

        # Check if index is integral
        if not self.is_integral_type(index_type):
            raise TypeCheckError("Array index must be integral type")

        return base_type

    def check_member_access(self, object_type: Type, member_name: str,
                           is_arrow: bool) -> Type:
        """
        Check member access operation.

        Args:
            object_type: Type of the object
            member_name: Name of the member
            is_arrow: True for ->, False for .

        Returns:
            Member type

        Raises:
            TypeCheckError: If access is invalid
        """
        # If arrow, dereference pointer first
        if is_arrow:
            if not isinstance(object_type, PointerType):
                raise TypeCheckError("Arrow operator requires pointer type")
            object_type = object_type.base_type

        # Get class name
        if isinstance(object_type, UserDefinedType):
            class_name = object_type.name
        else:
            raise TypeCheckError("Member access requires class/struct type")

        # Look up member
        member = self.type_registry.get_class_member(class_name, member_name)
        if not member:
            raise TypeCheckError(
                f"Class '{class_name}' has no member '{member_name}'"
            )

        return member.symbol_type

    def check_return_type(self, return_type: Optional[Type]) -> None:
        """
        Check if return type matches function's declared return type.

        Args:
            return_type: Type being returned (None for void return)

        Raises:
            TypeCheckError: If return type doesn't match
        """
        if self.current_function_return_type is None:
            raise TypeCheckError("Return statement outside of function")

        # Void function
        if isinstance(self.current_function_return_type, PrimitiveType) and \
           self.current_function_return_type.name == 'void':
            if return_type is not None:
                raise TypeCheckError("Void function cannot return a value")
            return

        # Non-void function
        if return_type is None:
            raise TypeCheckError("Non-void function must return a value")

        if not self.check_type_compatibility(return_type,
                                            self.current_function_return_type):
            raise TypeCheckError(
                "Return type incompatible with function return type"
            )

    def check_cast(self, source_type: Type, target_type: Type,
                  cast_kind: str) -> Type:
        """
        Check if cast is valid.

        Args:
            source_type: Type being cast from
            target_type: Type being cast to
            cast_kind: Kind of cast (static_cast, dynamic_cast, etc.)

        Returns:
            Target type

        Raises:
            TypeCheckError: If cast is invalid
        """
        if cast_kind == 'static_cast':
            # Static cast allows most conversions
            if isinstance(source_type, PrimitiveType) and \
               isinstance(target_type, PrimitiveType):
                return target_type

            if isinstance(source_type, PointerType) and \
               isinstance(target_type, PointerType):
                return target_type

            raise TypeCheckError(
                "static_cast cannot convert between these types"
            )

        elif cast_kind == 'dynamic_cast':
            # Dynamic cast requires polymorphic classes
            if not isinstance(source_type, PointerType) or \
               not isinstance(target_type, PointerType):
                raise TypeCheckError(
                    "dynamic_cast requires pointer types"
                )

            # Check inheritance relationship
            if isinstance(source_type.base_type, UserDefinedType) and \
               isinstance(target_type.base_type, UserDefinedType):
                return target_type

            raise TypeCheckError(
                "dynamic_cast requires class types"
            )

        elif cast_kind == 'const_cast':
            # Const cast only changes const/volatile
            return target_type

        elif cast_kind == 'reinterpret_cast':
            # Reinterpret cast allows most pointer conversions
            return target_type

        else:
            raise TypeCheckError(f"Unknown cast kind: {cast_kind}")

    def infer_type(self, expr: Expression) -> Type:
        """
        Infer the type of an expression (placeholder for full implementation).

        Args:
            expr: Expression node

        Returns:
            Inferred type
        """
        if isinstance(expr, IntegerLiteral):
            return PrimitiveType('int')

        if isinstance(expr, FloatLiteral):
            return PrimitiveType('double')

        if isinstance(expr, CharLiteral):
            return PrimitiveType('char')

        if isinstance(expr, StringLiteral):
            return PointerType(PrimitiveType('char', is_const=True))

        if isinstance(expr, BoolLiteral):
            return PrimitiveType('bool')

        if isinstance(expr, NullptrLiteral):
            return PrimitiveType('nullptr_t')

        # For more complex expressions, would need full visitor implementation
        raise TypeCheckError("Type inference not fully implemented for this expression")