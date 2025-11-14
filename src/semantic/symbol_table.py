"""
Synbol Table for the C++ compiler.
Manages variable, function, and class declarations with scope tracking.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto


class SymbolKind(Enum):
    """Types of symbols that can be stored."""
    VARIABLE = auto()
    FUNCTION = auto()
    CLASS = auto()
    ENUM = auto()
    TYPEDEF = auto()
    NAMESPACE = auto()
    TEMPLATE = auto()
    PARAMETER = auto()


@dataclass
class Symbol:
    """
    Represents a symbol in the symbol table.

    Attributes:
        name: Symbol name
        kind:Type of symbol (variable, function, class, etc.)
        symbol_type: The C++ type of the symbol (from AST Type nodes)
        scope_level: Nesting level of the scope where defined
        attributes: Additional symbol-specific information
    """
    name: str
    kind: SymbolKind
    symbol_type: Any  # Type from AST
    scope_level: int
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Symbol({self.name}, {self.kind.name}, level={self.scope_level})"

@dataclass
class FunctionSignature:
    """Represents a function signature for overload resolution."""
    return_type: Any
    parameter_types: List[Any]
    is_const: bool = False
    is_static: bool = False
    is_virtual: bool = False

    def matches(self, arg_types: List[Any]) -> bool:
        """Check if argument types match this signature."""
        if len(arg_types) != len(self.parameter_types):
            return False
        return True

class Scope:
    """
    Represents a single scope level.

    Scopes can be nested and each maintains its own symbol table.
    """

    def __init__(self, name: str = "", parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List['Scope'] = []

        if parent:
            parent.children.append(self)

    def define(self, symbol: Symbol) -> None:
        """Define a new symbol in this scope."""
        if symbol.name in self.symbols:
            raise Exception(f"Symbol '{symbol.name}' already defined in this scope.")
        self.symbols[symbol.name] = symbol

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope only."""
        return self.symbols.get(name)

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope and parent scopes."""
        symbol = self.lookup_local(name)
        if symbol:
            return symbol
        if self.parent:
            return self.parent.lookup(name)
        return None

    def __repr__(self) -> str:
        return f"Scope({self.name}, {len(self.symbols)} symbols)"

class SymbolTable:
    """
    Symbol table with scope management

    Manages nested scopes and symbol resolution for variables, functions,
    classes, and other C++ entities.
    """

    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.scope_level = 0

        # Namespace tracking
        self.current_namespace: List[str] = []

        # Class context (for member access)
        self.current_class: Optional[str] = None

        # Function overloads
        self.function_overloads: Dict[str, List[FunctionSignature]] = {}

    def enter_scope(self, name: str = "") -> None:
        """Enter a new scope."""
        new_scope = Scope(name, self.current_scope)
        self.current_scope = new_scope
        self.scope_level += 1

    def exit_scope(self) -> None:
        """Exit the current scope."""
        if self.current_scope.parent is None:
            raise Exception("Cannot exit global scope")
        self.current_scope = self.current_scope.parent
        self.scope_level -= 1

    def define(self, name: str, kind: SymbolKind, symbol_type: Any, **attributes) -> Symbol:
        """
        Define a new symbol in the current scope.

        Args:
            name: Symbol name
            kind: Symbol kind (variable, function, etc.)
            symbol_type: Type information from AST
            **attributes: Additional symbol attributes

        Returns:
            The created symbol

        Raises:
            Exception: If symbol already exists in current scope
        """
        # Check for redifinition in current scope
        if self.current_scope.lookup_local(name):
            raise Exception(f"Redifinition of '{name}' in scope '{self.current_scope.name}'")

        symbol = Symbol(
            name=name,
            kind=kind,
            symbol_type=symbol_type,
            scope_level=self.scope_level,
            attributes=attributes
        )

        self.current_scope.define(symbol)
        return symbol

    def define_function(self, name: str, return_type: Any, parameter_types: List[Any], **attributes) -> Symbol:
        """
        Define a function with support for overloading.

        Args:
            name: Function name
            return_type: Return type from AST
            parameter_types: List of parameter types
            **attributes: Additional attributes (is_const, is_static, etc.)

        Returns:
            The created Symbol
        """
        # Create function signature
        signature = FunctionSignature(
            return_type=return_type,
            parameter_types=parameter_types,
            is_const=attributes.get('is_const', False),
            is_static=attributes.get('is_static', False),
            is_virtual=attributes.get('is_virtual', False)
        )

        # Track overloads
        qualified_name = self.get_qualified_name(name)
        if qualified_name not in self.function_overloads:
            self.function_overloads[qualified_name] = []
        self.function_overloads[qualified_name].append(signature)

        # Define the symbol
        attributes['signature'] = signature
        attributes['overload_count'] = len(self.function_overloads[qualified_name])

        return self.define(name, SymbolKind.FUNCTION, return_type, **attributes)

    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol by name.

        Searches current scope and all parent scopes.

        Args:
            name: Symbol name to look up

        Returns:
            Symbol if found, None otherwise
        """
        return self.current_scope.lookup(name)

    def lookup_function(self, name: str, arg_types: List[Any]) -> Optional[Symbol]:
        """
        Look up a function with overload resolution.

        Args:
            name: Function name
            arg_types: Argument types for overload resolution

        Returns:
            Matching function symbol or None
        """
        qualified_name = self.get_qualified_name(name)

        if qualified_name in self.function_overloads:
            # Try to find matching overload
            for signature in self.function_overloads[qualified_name]:
                if signature.matches(arg_types):
                    return self.lookup(name)

        return self.lookup(name)

    def enter_namespace(self, name: str) -> None:
        """Enter a namespace scope."""
        self.current_namespace.append(name)
        self.enter_scope(f"namespace::{name}")

    def exit_namespace(self) -> None:
        """Exit a namespace scope."""
        if self.current_namespace:
            self.current_namespace.pop()
        self.exit_scope()

    def enter_class(self, name: str) -> None:
        """Enter a class scope."""
        self.current_class = name
        self.enter_scope(f"class::{name}")

    def exit_class(self) -> None:
        """Exit a class scope."""
        self.current_class = None
        self.exit_scope()

    def enter_function(self, name: str) -> None:
        """Enter a function scope."""
        self.enter_scope(f"function::{name}")

    def exit_function(self) -> None:
        """Exit a function scope."""
        self.exit_scope()

    def get_qualified_name(self, name: str) -> str:
        """Get the fully qualified name for a symbol."""
        parts = self.current_namespace + [name]
        return "::".join(parts)

    def is_global_scope(self) -> bool:
        """Check if we're in the global scope."""
        return self.current_scope == self.global_scope

    def get_scope_path(self) -> str:
        """Get the current scope path as a string."""
        path = []
        scope = self.current_scope
        while scope and scope.name:
            path.insert(0, scope.name)
            scope = scope.parent
        return "::".join(path) if path else "global"

    def dump(self) -> None:
        """Print the entire symbol table (for debugging)."""
        print("\n" + "=" * 80)
        print("SYMBOL TABLE")
        print("=" * 80)
        self._dump_scope(self.global_scope, 0)

    def _dump_scope(self, scope: Scope, indent: int) -> None:
        """Recursively dump a scope and its children."""
        prefix = "  " * indent
        print(f"{prefix}Scope: {scope.name or 'global'}")

        for symbol in scope.symbols.values():
            print(f"{prefix}  {symbol}")

        for child in scope.children:
            self._dump_scope(child, indent + 1)

class TypeRegistry:
    """
    Registry for user-defined types (classes, structs, enums).

    Tracks type definitions and supports type lookup and compatibility checking.
    """

    def __init__(self):
        self.types: Dict[str, Any] = {}  # name -> AST Type node
        self.class_members: Dict[str, Dict[str, Symbol]] = {}  # class_name -> members
        self.class_bases: Dict[str, List[str]] = {}  # class_name -> base classes

    def register_type(self, name: str, type_node: Any) -> None:
        """Register a user-defined type."""
        if name in self.types:
            raise Exception(f"Type '{name}' already defined")
        self.types[name] = type_node

    def register_class(self, name: str, type_node: Any,
                           base_classes: List[str] = None) -> None:
        """Register a class or struct."""
        self.register_type(name, type_node)
        self.class_members[name] = {}
        self.class_bases[name] = base_classes or []

    def add_class_member(self, class_name: str, member: Symbol) -> None:
        """Add a member to a class."""
        if class_name not in self.class_members:
            raise Exception(f"Class '{class_name}' not registered")

        if member.name in self.class_members[class_name]:
            raise Exception(
                f"Member '{member.name}' already exists in class '{class_name}'"
            )

        self.class_members[class_name][member.name] = member

    def get_class_member(self, class_name: str, member_name: str) -> Optional[Symbol]:
        """Get a member of a class."""
        if class_name not in self.class_members:
            return None
        return self.class_members[class_name].get(member_name)

    def lookup_type(self, name: str) -> Optional[Any]:
        """Look up a type by name."""
        return self.types.get(name)

    def is_class(self, name: str) -> bool:
        """Check if a type is a class."""
        return name in self.class_members

    def get_base_classes(self, class_name: str) -> List[str]:
        """Get base classes of a class."""
        return self.class_bases.get(class_name, [])

    def is_derived_from(self, derived: str, base: str) -> bool:
        """Check if one class is derived from another."""
        if derived == base:
            return True

        bases = self.get_base_classes(derived)
        for b in bases:
            if self.is_derived_from(b, base):
                return True

        return False

    def dump(self) -> None:
        """Print all registered types (for debugging)."""
        print("\n" + "=" * 80)
        print("TYPE REGISTRY")
        print("=" * 80)

        for name in self.types:
            print(f"Type: {name}")
            if name in self.class_members:
                print(f"  Members: {len(self.class_members[name])}")
                for member in self.class_members[name].values():
                    print(f"    {member}")
            if name in self.class_bases and self.class_bases[name]:
                print(f"  Base classes: {', '.join(self.class_bases[name])}")