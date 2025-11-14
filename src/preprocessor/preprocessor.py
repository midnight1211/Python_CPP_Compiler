"""
Preprocessor for C++.
Handles #include, #define, #ifdef, #ifndef, #if, #elif, #else, #endig, #undef, #pragma
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass


class PreprocessorError(Exception):
    """Exception raise for"""

    def __init__(self, message: str, line: int = 0):
        self.message = message
        self.line = line
        super().__init__(f"Preprocessor error at line {line}: {message}")


@dataclass
class Macro:
    """Represents a preprocessor macro."""
    name: str
    value: str
    parameters: Optional[List[str]] = None
    is_function_like: bool = False

    def expand(self, args: List[str] = None) -> str:
        """Expand the macro with given arguments."""
        if not self.is_function_like:
            return self.value

        if args is None or len(args) != len(self.parameters):
            raise PreprocessorError(f"Macro {self.name} expects {len(self.parameters)} arguments")

        result = self.value
        for param, arg in zip(self.parameters, args):
            result = result.replace(param, arg)

        return result

class Preprocessor:
    """
    C++ Preprocessor.

    Handles:
    - #include directives
    - #define macros (object-like and function-like)
    - Conditional compilation (#ifndef, #ifdef, #if, #elif, #else, #endif)
    - #undef
    - #pragma
    - Predefined macros (__FILE__, __LINE__, __DATE__, __TIME__)
    """

    def __init__(self, include_paths: List[str] = None):
        """
        Initialize preprocessor.

        Args:
            include_paths: List of directories to search for includes
        """
        self.include_paths = include_paths or ['.']
        self.macros: Dict[str, Macro] = {}
        self.included_files: Set[str] = set()
        self.current_file = "<stdin>"
        self.current_line = 0

        # Predefined macros
        self._define_predefined_macros()

    def _define_predefined_macros(self):
        """Define standard predefined macros."""
        import datetime

        now = datetime.datetime.now()

        # Standard predefined macros
        self.macros['__cplusplus'] = Macro('__cplusplus', '202002L')
        self.macros['__STDC__'] = Macro('__STDC__', '1')
        