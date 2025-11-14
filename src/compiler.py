"""
Main Compiler Driver.
Orchestrates the entire compilation process from source to assembly.
"""

from typing import Optional
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .semantic import SemanticAnalyzer, SemanticError
from .ir import IRGenerator, IRGeneratorError, optimize_ir
from .codegen import CodeGenerator, CodeGeneratorError


class CompilerError(Exception):
    """Base exception for compiler errors."""
    pass


class Compiler:
    """
    Main compiler class.

    Orchestrates the compilation pipeline:
    1. Lexical analysis (source → tokens)
    2. Syntax analysis (tokens → AST)
    3. Semantic analysis (AST validation)
    4. IR generation (AST → IR)
    5. Optimization (IR → optimized IR)
    6. Code generation (IR → assembly)
    """

    def __init__(self,
                 optimization_level: int = 2,
                 target: str = "x86_64",
                 debug: bool = False):
        """
        Initialize compiler.

        Args:
            optimization_level: 0-3 (0=none, 3=aggressive)
            target: Target architecture
            debug: Enable debug output
        """
        self.optimization_level = optimization_level
        self.target = target
        self.debug = debug

        # Compilation artifacts
        self.source_code: Optional[str] = None
        self.tokens = None
        self.ast = None
        self.ir_program = None
        self.assembly_code: Optional[str] = None

        # Statistics
        self.stats = {
            'tokens': 0,
            'ast_nodes': 0,
            'ir_instructions': 0,
            'assembly_lines': 0,
        }

    def compile(self, source_code: str, filename: str = "<stdin>") -> str:
        """
        Compile source code to assembly.

        Args:
            source_code: C++ source code
            filename: Source filename (for error reporting)

        Returns:
            Assembly code as string

        Raises:
            CompilerError: If compilation fails
        """
        self.source_code = source_code

        try:
            # Phase 1: Lexical Analysis
            if self.debug:
                print("Phase 1: Lexical Analysis...")
            self.tokens = self._lex(source_code, filename)
            self.stats['tokens'] = len(self.tokens)

            # Phase 2: Syntax Analysis
            if self.debug:
                print("Phase 2: Syntax Analysis...")
            self.ast = self._parse(self.tokens)
            self.stats['ast_nodes'] = len(self.ast.declarations)

            # Phase 3: Semantic Analysis
            if self.debug:
                print("Phase 3: Semantic Analysis...")
            self._analyze(self.ast)

            # Phase 4: IR Generation
            if self.debug:
                print("Phase 4: IR Generation...")
            self.ir_program = self._generate_ir(self.ast)
            self.stats['ir_instructions'] = sum(
                len(func.instructions) for func in self.ir_program.functions
            )

            # Phase 5: Optimization
            if self.optimization_level > 0:
                if self.debug:
                    print(f"Phase 5: Optimization (level {self.optimization_level})...")
                self.ir_program = self._optimize(self.ir_program)
                self.stats['ir_instructions'] = sum(
                    len(func.instructions) for func in self.ir_program.functions
                )

            # Phase 6: Code Generation
            if self.debug:
                print("Phase 6: Code Generation...")
            self.assembly_code = self._generate_code(self.ir_program)
            self.stats['assembly_lines'] = len(self.assembly_code.split('\n'))

            if self.debug:
                print("\nCompilation successful!")
                self.print_stats()

            return self.assembly_code

        except (LexerError, ParserError, SemanticError,
                IRGeneratorError, CodeGeneratorError) as e:
            raise CompilerError(str(e)) from e

    def compile_file(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Compile a source file.

        Args:
            input_file: Input source file path
            output_file: Output assembly file path (optional)

        Returns:
            Assembly code
        """
        # Read source file
        with open(input_file, 'r') as f:
            source_code = f.read()

        # Compile
        assembly = self.compile(source_code, input_file)

        # Write output if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(assembly)
            if self.debug:
                print(f"Assembly written to {output_file}")

        return assembly

    def _lex(self, source_code: str, filename: str):
        """Phase 1: Lexical analysis."""
        lexer = Lexer(source_code, filename)
        return lexer.tokenize()

    def _parse(self, tokens):
        """Phase 2: Syntax analysis."""
        parser = Parser(tokens)
        return parser.parse()

    def _analyze(self, ast):
        """Phase 3: Semantic analysis."""
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)

        if not success:
            # Collect all errors
            errors = '\n'.join(analyzer.errors)
            raise SemanticError(f"Semantic analysis failed:\n{errors}")

    def _generate_ir(self, ast):
        """Phase 4: IR generation."""
        generator = IRGenerator()
        return generator.generate(ast)

    def _optimize(self, ir_program):
        """Phase 5: Optimization."""
        return optimize_ir(ir_program, level=self.optimization_level)

    def _generate_code(self, ir_program):
        """Phase 6: Code generation."""
        generator = CodeGenerator(target=self.target)
        return generator.generate(ir_program)

    def print_stats(self) -> None:
        """Print compilation statistics."""
        print("\n" + "=" * 60)
        print("COMPILATION STATISTICS")
        print("=" * 60)
        print(f"Tokens:           {self.stats['tokens']}")
        print(f"AST nodes:        {self.stats['ast_nodes']}")
        print(f"IR instructions:  {self.stats['ir_instructions']}")
        print(f"Assembly lines:   {self.stats['assembly_lines']}")
        print(f"Optimization:     Level {self.optimization_level}")
        print(f"Target:           {self.target}")
        print("=" * 60)

    def get_tokens(self):
        """Get the token list from lexer."""
        return self.tokens

    def get_ast(self):
        """Get the abstract syntax tree."""
        return self.ast

    def get_ir(self):
        """Get the intermediate representation."""
        return self.ir_program

    def get_assembly(self):
        """Get the generated assembly code."""
        return self.assembly_code


def compile_source(source_code: str,
                   optimization_level: int = 2,
                   debug: bool = False) -> str:
    """
    Convenience function to compile source code.

    Args:
        source_code: C++ source code
        optimization_level: Optimization level (0-3)
        debug: Enable debug output

    Returns:
        Assembly code
    """
    compiler = Compiler(
        optimization_level=optimization_level,
        debug=debug
    )
    return compiler.compile(source_code)


def compile_file(input_file: str,
                 output_file: Optional[str] = None,
                 optimization_level: int = 2,
                 debug: bool = False) -> str:
    """
    Convenience function to compile a file.

    Args:
        input_file: Input source file
        output_file: Output assembly file (optional)
        optimization_level: Optimization level (0-3)
        debug: Enable debug output

    Returns:
        Assembly code
    """
    compiler = Compiler(
        optimization_level=optimization_level,
        debug=debug
    )
    return compiler.compile_file(input_file, output_file)