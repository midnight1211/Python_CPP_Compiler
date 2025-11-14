# Compiler Architecture

## Overview

This document describes the architecture of the C++ compiler, including the design decisions, data flow, and component interactions.

## High-Level Architecture

```
┌─────────────────┐
│  Source Code    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Lexer       │  Tokenization
│  (lexer.py)     │  - Scan characters
└────────┬────────┘  - Generate tokens
         │            - Track positions
         ▼
┌─────────────────┐
│     Parser      │  Syntax Analysis
│  (parser.py)    │  - Build AST
└────────┬────────┘  - Check syntax
         │            - Error recovery
         ▼
┌─────────────────┐
│   Semantic      │  Semantic Analysis
│  Analyzer       │  - Type checking
│ (analyzer.py)   │  - Symbol tables
└────────┬────────┘  - Scope resolution
         │
         ▼
┌─────────────────┐
│  IR Generator   │  IR Generation
│(ir_generator.py)│  - Three-address code
└────────┬────────┘  - Control flow graphs
         │
         ▼
┌─────────────────┐
│  IR Optimizer   │  Optimization
│(ir_optimizer.py)│  - Constant folding
└────────┬────────┘  - Dead code elimination
         │            - Copy propagation
         ▼
┌─────────────────┐
│ Code Generator  │  Code Generation
│(code_generator  │  - Register allocation
│      .py)       │  - Instruction selection
└────────┬────────┘  - Assembly output
         │
         ▼
┌─────────────────┐
│  Assembly Code  │
└─────────────────┘
```

## Component Details

### 1. Lexer (Lexical Analyzer)

**Location**: `src/lexer/`

**Purpose**: Converts source code text into a stream of tokens.

**Key Classes**:
- `Lexer`: Main lexer class
- `Token`: Token representation with type, value, position
- `TokenType`: Enum of all token types

**Design Decisions**:
- Hand-written lexer (not generated) for educational clarity
- Single-pass scanning with lookahead
- Line/column tracking for error reporting
- Supports C++20 keywords and operators

**Algorithm**:
1. Read character by character
2. Use state machine to recognize patterns
3. Skip whitespace and comments
4. Emit tokens with position information

### 2. Parser (Syntax Analyzer)

**Location**: `src/parser/`

**Purpose**: Converts token stream into Abstract Syntax Tree (AST).

**Key Classes**:
- `Parser`: Recursive descent parser
- `ASTNode`: Base class for all AST nodes
- Various node types: `Expression`, `Statement`, `Declaration`

**Design Decisions**:
- Recursive descent parsing (top-down)
- LL(1) grammar with limited lookahead
- Explicit operator precedence handling
- Error recovery with synchronization points

**Grammar**:
- Defined in `grammar.txt`
- EBNF notation
- Left-recursive rules eliminated
- Ambiguity resolved by precedence

### 3. Semantic Analyzer

**Location**: `src/semantic/`

**Purpose**: Validates semantic correctness of the AST.

**Key Classes**:
- `SemanticAnalyzer`: Main analyzer using Visitor pattern
- `SymbolTable`: Manages scopes and symbols
- `TypeChecker`: Validates types
- `TypeRegistry`: Tracks user-defined types

**Design Decisions**:
- Visitor pattern for AST traversal
- Hierarchical symbol tables for nested scopes
- Separate type registry for classes/enums
- Function overload tracking

**Checks Performed**:
- Undeclared variable usage
- Type compatibility
- Duplicate declarations
- Break/continue in proper context
- Return type matching
- Class member access

### 4. IR Generator

**Location**: `src/ir/`

**Purpose**: Converts AST to intermediate representation.

**Key Classes**:
- `IRGenerator`: AST to IR converter
- `IRInstruction`: Three-address code instruction
- `IRBuilder`: Helper for building IR

**Design Decisions**:
- Three-address code format (result = arg1 op arg2)
- Unlimited virtual registers (temporaries)
- Explicit control flow with labels and jumps
- Platform-independent representation

**IR Format**:
```
t1 = a + b      # Binary operation
t2 = -t1        # Unary operation
x = t2          # Assignment
if t2 goto L1   # Conditional jump
goto L2         # Unconditional jump
L1:             # Label
return t2       # Return
```

### 5. IR Optimizer

**Location**: `src/ir/`

**Purpose**: Optimizes intermediate representation.

**Key Classes**:
- `IROptimizer`: Main optimizer
- `PeepholeOptimizer`: Local optimizations

**Design Decisions**:
- Multiple optimization passes
- Iterative until fixed point
- Configurable optimization levels (0-3)

**Optimizations**:
1. **Constant Folding**: Evaluate constants at compile time
   - `t1 = 2 + 3` → `t1 = 5`

2. **Constant Propagation**: Replace variables with constants
   - `x = 5; y = x` → `x = 5; y = 5`

3. **Copy Propagation**: Replace copies with original
   - `x = y; z = x` → `x = y; z = y`

4. **Dead Code Elimination**: Remove unused code
   - Remove instructions with unused results

5. **Arithmetic Simplification**: Simplify expressions
   - `x * 1` → `x`
   - `x + 0` → `x`
   - `x * 0` → `0`

### 6. Code Generator

**Location**: `src/codegen/`

**Purpose**: Generates target assembly code (x86-64).

**Key Classes**:
- `CodeGenerator`: Main code generator
- `RegisterAllocator`: Register allocation

**Design Decisions**:
- Target: x86-64 System V ABI
- Stack-based allocation with register optimization
- Caller-saved vs callee-saved register distinction
- Simplified calling convention

**Register Usage**:
- `rax`: Return values, temporaries
- `rbx`, `rcx`, `rdx`: Temporaries
- `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9`: Parameter passing
- `rbp`: Frame pointer
- `rsp`: Stack pointer

**Assembly Generation**:
1. Function prologue: Set up stack frame
2. Allocate local variables on stack
3. Generate instructions for IR operations
4. Function epilogue: Restore stack and return

## Data Structures

### Symbol Table

```python
{
    'global': {
        'x': Symbol(name='x', type=int, scope=0),
        'main': Symbol(name='main', type=function, scope=0)
    },
    'main': {
        'y': Symbol(name='y', type=int, scope=1)
    }
}
```

### AST Structure

```
Program
├── FunctionDeclaration (main)
│   ├── return_type: int
│   ├── parameters: []
│   └── body: CompoundStatement
│       ├── VariableDeclaration (x)
│       │   ├── type: int
│       │   └── initializer: IntegerLiteral(5)
│       └── ReturnStatement
│           └── Identifier(x)
```

### IR Structure

```
Function: main
    x = 5
    return x
```

## Error Handling

### Lexer Errors
- Invalid characters
- Unterminated strings/comments
- Malformed numbers

### Parser Errors
- Unexpected tokens
- Missing semicolons
- Unmatched brackets
- Syntax violations

### Semantic Errors
- Undeclared variables
- Type mismatches
- Duplicate declarations
- Invalid operations

### IR Generation Errors
- Unsupported constructs
- Invalid transformations

### Code Generation Errors
- Register allocation failures
- Invalid instructions

## Performance Characteristics

### Time Complexity
- Lexer: O(n) where n = source length
- Parser: O(n) where n = token count
- Semantic: O(n) where n = AST nodes
- IR Gen: O(n) where n = AST nodes
- Optimizer: O(n * p) where p = passes
- Codegen: O(n) where n = IR instructions

### Space Complexity
- Lexer: O(n) for token list
- Parser: O(d) for recursion depth
- Semantic: O(s) for symbol table size
- IR: O(i) for instruction count
- Codegen: O(i) for assembly size

## Extension Points

### Adding New Optimizations
1. Create optimization method in `IROptimizer`
2. Add to optimization pipeline
3. Test on representative programs

### Adding New Target Architecture
1. Create new module in `src/codegen/targets/`
2. Implement code generation methods
3. Update `CodeGenerator` to support target

### Adding New Language Features
1. Add tokens to `TokenType`
2. Update lexer patterns
3. Add AST nodes
4. Update parser grammar
5. Add semantic checks
6. Generate appropriate IR
7. Handle in code generation

## Testing Strategy

### Unit Tests
- Test each component independently
- Mock dependencies
- Cover edge cases

### Integration Tests
- Test component interactions
- End-to-end compilation
- Compare outputs

### Regression Tests
- Prevent breaking changes
- Maintain test suite
- Automated testing

## Future Improvements

1. **Preprocessor**: Add #include, #define support
2. **Templates**: Full template instantiation
3. **Link-Time Optimization**: Cross-function optimization
4. **Better Error Messages**: Show context, suggestions
5. **IDE Integration**: Language server protocol
6. **Debugging Support**: DWARF debug information
7. **More Targets**: ARM, RISC-V, WASM
8. **Incremental Compilation**: Faster rebuilds
9. **Parallel Compilation**: Multi-threaded processing
10. **JIT Compilation**: Runtime code generation