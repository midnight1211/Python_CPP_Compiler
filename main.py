#!/usr/bin/env python3
"""
Main entry point for the C++ compiler.
Command-line interface for compiling C++ source files.
"""

import sys
import argparse
from pathlib import Path

from src.compiler import Compiler, CompilerError


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='C++ Compiler - Compiles C++ source to x86-64 assembly',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s program.cpp                    # Compile to program.s
  %(prog)s program.cpp -o output.s        # Specify output file
  %(prog)s program.cpp -O3                # Maximum optimization
  %(prog)s program.cpp --debug            # Show compilation phases
  %(prog)s program.cpp --show-tokens      # Display tokens
  %(prog)s program.cpp --show-ast         # Display AST
  %(prog)s program.cpp --show-ir          # Display IR
        """
    )

    # Input/output
    parser.add_argument('input', help='Input C++ source file')
    parser.add_argument('-o', '--output', help='Output assembly file')

    # Optimization
    parser.add_argument('-O', '--optimize', type=int, default=2, choices=[0, 1, 2, 3],
                        help='Optimization level (default: 2)')
    parser.add_argument('-O0', action='store_const', const=0, dest='optimize',
                        help='No optimization')
    parser.add_argument('-O1', action='store_const', const=1, dest='optimize',
                        help='Basic optimization')
    parser.add_argument('-O2', action='store_const', const=2, dest='optimize',
                        help='Standard optimization')
    parser.add_argument('-O3', action='store_const', const=3, dest='optimize',
                        help='Aggressive optimization')

    # Debug options
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')
    parser.add_argument('--show-tokens', action='store_true',
                        help='Display tokens')
    parser.add_argument('--show-ast', action='store_true',
                        help='Display AST')
    parser.add_argument('--show-ir', action='store_true',
                        help='Display IR')
    parser.add_argument('--show-optimized-ir', action='store_true',
                        help='Display optimized IR')
    parser.add_argument('--stats', action='store_true',
                        help='Show compilation statistics')

    # Target
    parser.add_argument('--target', default='x86_64',
                        help='Target architecture (default: x86_64)')

    args = parser.parse_args()

    # Check input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        return 1

    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = input_path.with_suffix('.s')

    try:
        # Create compiler
        compiler = Compiler(
            optimization_level=args.optimize,
            target=args.target,
            debug=args.debug
        )

        # Read source
        with open(input_path, 'r') as f:
            source_code = f.read()

        print(f"Compiling {args.input}...")

        # Compile
        assembly = compiler.compile(source_code, str(input_path))

        # Display intermediate representations if requested
        if args.show_tokens:
            print("\n" + "=" * 80)
            print("TOKENS")
            print("=" * 80)
            for i, token in enumerate(compiler.get_tokens(), 1):
                if token.type.name != 'EOF':
                    print(f"{i:4d}. {token}")

        if args.show_ast:
            print("\n" + "=" * 80)
            print("ABSTRACT SYNTAX TREE")
            print("=" * 80)
            # Would need AST printer implementation
            print(f"AST with {len(compiler.get_ast().declarations)} declarations")

        if args.show_ir:
            print("\n" + "=" * 80)
            print("INTERMEDIATE REPRESENTATION")
            print("=" * 80)
            # Get IR before optimization
            from src.ir import IRGenerator
            ir_gen = IRGenerator()
            unoptimized_ir = ir_gen.generate(compiler.get_ast())
            print(unoptimized_ir)

        if args.show_optimized_ir:
            print("\n" + "=" * 80)
            print("OPTIMIZED INTERMEDIATE REPRESENTATION")
            print("=" * 80)
            print(compiler.get_ir())

        # Write output
        with open(output_file, 'w') as f:
            f.write(assembly)

        print(f"✓ Compilation successful!")
        print(f"  Output written to: {output_file}")

        if args.stats or args.debug:
            compiler.print_stats()

        return 0

    except CompilerError as e:
        print(f"\n✗ Compilation failed:", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error:", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())