# API Reference

Complete
API
documentation
for the C + + compiler.

## Main Compiler API

### `Compiler` Class

Main
compiler


class that orchestrates the entire compilation pipeline.


```python
from src.compiler import Compiler

compiler = Compiler(
    optimization_level=2,  # 0-3
    target="x86_64",  # Target architecture
    debug=False  # Enable debug output
)
```

#### Methods

** `compile(source_code: str, filename: str = "<stdin>") -> str
` **

Compile
source
code
to
assembly.

- ** Parameters: **
- `source_code`: C + + source
code
string
- `filename`: Source
filename
for error reporting
    - ** Returns: ** Assembly
code as string
- ** Raises: ** `CompilerError` if compilation
fails

```python
assembly = compiler.compile("""
int main() {
    return 42;
}
""")
```

** `compile_file(input_file: str, output_file: str = None) -> str
` **

Compile
a
source
file.

- ** Parameters: **
- `input_file`: Path
to
input
C + + file
- `output_file`: Path
to
output
assembly
file(optional)
- ** Returns: ** Assembly
code as string

```python
assembly = compiler.compile_file("program.cpp", "program.s")
```

** `get_tokens() -> List[Token]
` **

Get
the
token
list
from lexer phase.

** `get_ast() -> Program
` **

Get
the
Abstract
Syntax
Tree.

** `get_ir() -> IRProgram
` **

Get
the
Intermediate
Representation.

** `get_assembly() -> str
` **

Get
the
generated
assembly
code.

** `print_stats() -> None
` **

Print
compilation
statistics.

#### Attributes

- `optimization_level`: Current
optimization
level(0 - 3)
- `target`: Target
architecture
- `debug`: Debug
mode
flag
- `stats`: Dictionary
of
compilation
statistics

---

## Lexer API

### `Lexer` Class

Lexical
analyzer
that
converts
source
code
into
tokens.

```python
from src.lexer import Lexer

lexer = Lexer(source_code, filename="program.cpp")
```

#### Methods

** `tokenize() -> List[Token]
` **

Tokenize
the
source
code.

- ** Returns: ** List
of
Token
objects
- ** Raises: ** `LexerError` if lexical
errors
occur

```python
tokens = lexer.tokenize()
for token in tokens:
    print(token.type, token.value, token.line, token.column)
```

** `get_next_token() -> Token
` **

Get
the
next
token
from the source.

- ** Returns: ** Next
Token

### `Token` Class

Represents
a
single
token.

#### Attributes

- `type`: TokenType
enum
value
- `value`: String
value
of
the
token
- `line`: Line
number
- `column`: Column
number

#### Methods

- `is_keyword() -> bool
`: Check if token is a
keyword
- `is_operator() -> bool
`: Check if token is an
operator
- `is_literal() -> bool
`: Check if token is a
literal
- `is_delimiter() -> bool
`: Check if token is a
delimiter
- `matches(token_type: TokenType) -> bool
`: Check if matches
type

### `TokenType` Enum

Enumeration
of
all
token
types.

```python
from src.lexer import TokenType

TokenType.INT  # int keyword
TokenType.IDENTIFIER  # variable/function name
TokenType.PLUS  # + operator
TokenType.SEMICOLON  # ; delimiter
```

---

## Parser API

### `Parser` Class

Recursive
descent
parser
that
builds
an
AST
from tokens.

```python
from src.parser import Parser

parser = Parser(tokens)
```

#### Methods

** `parse() -> Program
` **

Parse
tokens
into
an
Abstract
Syntax
Tree.

- ** Returns: ** Program
AST
node
- ** Raises: ** `ParserError` if syntax
errors
occur

```python
ast = parser.parse()
```

### AST Node Classes

All
AST
nodes
inherit
from

`ASTNode`
base


class .


#### `Program`

Root
node
of
the
AST.

- `declarations`: List
of
top - level
declarations

#### `FunctionDeclaration`

Function
declaration
node.

- `return_type`: Return
type
- `name`: Function
name
- `parameters`: List
of
Parameter
nodes
- `body`: CompoundStatement or None
- `is_inline`, `is_static`, `is_virtual`: Flags

#### `VariableDeclaration`

Variable
declaration
node.

- `var_type`: Variable
type
- `name`: Variable
name
- `initializer`: Expression or None

#### `ClassDeclaration`

Class / struct
declaration.

- `name`: Class
name
- `base_classes`: List
of
base


class names
    - `members`: List
    of
    member
    declarations


#### Expression Nodes

- `BinaryExpression`: Binary
operations(a + b)
- `UnaryExpression`: Unary
operations(-a, ++a)
- `AssignmentExpression`: Assignments(a=b)
- `CallExpression`: Function
calls(func(args))
- `Identifier`: Variable / function
names
- `IntegerLiteral`, `FloatLiteral`, etc.: Literal
values

---

## Semantic Analysis API

### `SemanticAnalyzer` Class

Semantic
analyzer
for type checking and validation.

```python
from src.semantic import SemanticAnalyzer

analyzer = SemanticAnalyzer()
```

#### Methods

** `analyze(program: Program) -> bool
` **

Analyze
an
AST
for semantic correctness.

- ** Parameters: ** `program` - Program
AST
node
- ** Returns: ** True if analysis
succeeded, False
otherwise

```python
success = analyzer.analyze(ast)
if not success:
    analyzer.print_errors()
```

** `print_errors() -> None
` **

Print
all
semantic
errors.

** `dump_symbol_table() -> None
` **

Print
the
symbol
table
for debugging.

### `SymbolTable` Class

Manages
symbols and scopes.

#### Methods

- `define(name, kind, symbol_type, **attributes) -> Symbol
`: Define
symbol
- `lookup(name) -> Optional[Symbol]
`: Look
up
symbol
- `enter_scope(name)`: Enter
new
scope
- `exit_scope()`: Exit
current
scope
- `enter_namespace(name)`: Enter
namespace
- `enter_class(name)`: Enter


class scope
    - `enter_function(name)`: Enter
    function
    scope


### `TypeChecker` Class

Type
checking and inference.

#### Methods

- `check_type_compatibility(source, target) -> bool
`: Check
compatibility
- `get_binary_operation_type(left, op, right) -> Type
`: Infer
binary
op
type
- `get_unary_operation_type(op, operand) -> Type
`: Infer
unary
op
type
- `check_function_call(func_type, arg_types, param_types) -> Type
`: Check
call

---

## IR API

### `IRGenerator` Class

Generates
intermediate
representation
from AST.

```python
from src.ir import IRGenerator

ir_gen = IRGenerator()
```

#### Methods

** `generate(program: Program) -> IRProgram
` **

Generate
IR
from AST.

- ** Parameters: ** `program` - Program
AST
node
- ** Returns: ** IRProgram

```python
ir_program = ir_gen.generate(ast)
print(ir_program)
```

### `IRProgram` Class

Complete
IR
program.

#### Attributes

- `functions`: List
of
IRFunction
objects
- `global_vars`: List
of
global variables
- `string_literals`: List
of
string
literals

### `IRFunction` Class

IR
function
representation.

#### Attributes

- `name`: Function
name
- `parameters`: List
of
parameters
- `return_type`: Return
type
- `instructions`: List
of
IRInstruction
objects
- `local_vars`: List
of
local
variables

### `IRInstruction` Class

Three - address
code
instruction.

#### Attributes

- `opcode`: IROpcode
enum
value
- `result`: Result
operand(IRValue)
- `arg1`, `arg2`, `arg3`: Argument
operands
- `label`: Label
for control flow

### `IROpcode` Enum

IR
instruction
opcodes.

```python
IROpcode.ADD  # Addition
IROpcode.SUB  # Subtraction
IROpcode.ASSIGN  # Assignment
IROpcode.GOTO  # Unconditional jump
IROpcode.IF_FALSE  # Conditional jump
IROpcode.CALL  # Function call
IROpcode.RETURN  # Return statement
```

### Optimization

** `optimize_ir(program: IRProgram, level: int = 2) -> IRProgram
` **

Optimize
IR
program.

- ** Parameters: **
- `program`: IR
program
to
optimize
- `level`: Optimization
level(0 - 3)
- ** Returns: ** Optimized
IR
program

```python
from src.ir import optimize_ir

optimized = optimize_ir(ir_program, level=3)
```

---

## Code Generation API

### `CodeGenerator` Class

Generates
target
assembly
code
from IR.

```python
from src.codegen import CodeGenerator

codegen = CodeGenerator(target="x86_64")
```

#### Methods

** `generate(program: IRProgram) -> str
` **

Generate
assembly
code.

- ** Parameters: ** `program` - IR
program
- ** Returns: ** Assembly
code as string

```python
assembly = codegen.generate(ir_program)
```

### `RegisterAllocator` Class

Register
allocation
for code generation.

```python
from src.codegen import RegisterAllocator

allocator = RegisterAllocator(available_registers)
```

#### Methods

** `allocate(function: IRFunction) -> Dict[str, str]
` **

Allocate
registers
for a function.

- ** Parameters: ** `function` - IR
function
- ** Returns: ** Mapping
of
variables
to
registers / stack
locations

---

## Convenience Functions

### `compile_source(source_code, optimization_level=2, debug=False) -> str`

Quick
compilation
of
source
code.

```python
from src.compiler import compile_source

assembly = compile_source("""
int main() {
    return 42;
}
""", optimization_level=2)
```

### `compile_file(input_file, output_file=None, optimization_level=2, debug=False) -> str`

Quick
compilation
of
a
file.

```python
from src.compiler import compile_file

assembly = compile_file("program.cpp", "program.s", optimization_level=3)
```

---

## Error Classes

### `CompilerError`

Base
exception
for all compiler errors.

### `LexerError`

Raised
for lexical analysis errors.

- Attributes: `message`, `line`, `column`

### `ParserError`

Raised
for syntax errors.

- Attributes: `message`, `token`

### `SemanticError`

Raised
for semantic analysis errors.

- Attributes: `message`, `node`

### `IRGeneratorError`

Raised
for IR generation errors.

### `CodeGeneratorError`

Raised
for code generation errors.

---

## Usage Examples

### Complete Compilation Pipeline

```python
from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.ir import IRGenerator, optimize_ir
from src.codegen import CodeGenerator

source = """
int add(int a, int b) {
    return a + b;
}
"""

# 1. Lexical analysis
lexer = Lexer(source)
tokens = lexer.tokenize()

# 2. Parsing
parser = Parser(tokens)
ast = parser.parse()

# 3. Semantic analysis
analyzer = SemanticAnalyzer()
analyzer.analyze(ast)

# 4. IR generation
ir_gen = IRGenerator()
ir_program = ir_gen.generate(ast)

# 5. Optimization
optimized = optimize_ir(ir_program, level=2)

# 6. Code generation
codegen = CodeGenerator()
assembly = codegen.generate(optimized)

print(assembly)
```

### Using the Main Compiler

```python
from src.compiler import Compiler

compiler = Compiler(optimization_level=3, debug=True)

source = """
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
"""

assembly = compiler.compile(source)
compiler.print_stats()

# Access intermediate stages
tokens = compiler.get_tokens()
ast = compiler.get_ast()
ir = compiler.get_ir()
```

---

## Type Definitions

### Type System

C + + types
are
represented
by
these
classes:

- `PrimitiveType`: Built - in types(int, float, etc.)
- `PointerType`: Pointer
types
- `ReferenceType`: Reference
types
- `ArrayType`: Array
types
- `UserDefinedType`: Classes, structs, enums

### Symbol Information

Symbols
are
stored
with:

- `name`: Symbol
name
- `kind`: SymbolKind(VARIABLE, FUNCTION, CLASS, etc.)
- `symbol_type`: Type
information
- `scope_level`: Nesting
level
- `attributes`: Additional
metadata

---

## Configuration

### Optimization Levels

- ** -O0 **: No
optimization
- Fastest
compilation
- Easiest
to
debug

- ** -O1 **: Basic
optimization
- Constant
folding
- Dead
code
elimination

- ** -O2 **: Standard
optimization(default)
- All - O1
optimizations
- Constant
propagation
- Copy
propagation

- ** -O3 **: Aggressive
optimization
- All - O2
optimizations
- Peephole
optimizations
- Multiple
passes

### Target Architectures

Currently
supported:
- `x86_64`: 64 - bit
x86(default)

Future
targets:
- `x86`: 32 - bit
x86
- `arm64`: 64 - bit
ARM
- `riscv`: RISC - V

---

## Best Practices

1. ** Error
Handling **: Always
wrap
compilation in
try-except
2. ** Debugging **: Use
`debug = True
`
for detailed output
    3. ** Optimization **: Start
    with -O2, use - O0 for debugging
4. ** Large
Programs **: Consider
incremental
compilation
5. ** Memory **: Parser
recursion
depth
may
limit
very
nested
code

---

## Performance Tips

1.
Reuse
`Compiler`
objects
for multiple files
    2.
    Use
    higher
    optimization
    levels
    for production
        3.
    Cache
    tokenization
    results if parsing
    multiple
    times
4.
Profile
with `scripts / benchmark.py`

---

## Extending the Compiler

### Adding a New Optimization

1.
Add
method
to
`IROptimizer`


class
    2.
    Call
    it
    from
    `optimize_function()`


3.
Test
with representative programs

### Adding a New AST Node

1.
Define
node


class in `ast_nodes.py`


2.
Add
parser
method in `parser.py`
3.
Add
visitor
method in `SemanticAnalyzer`
4.
Add
visitor
method in `IRGenerator`
5.
Handle in `CodeGenerator` if needed

### Adding a New Target

1.
Create
new
module in `src / codegen / targets / `
2.
Implement
register
set and calling
convention
3.
Implement
instruction
selection
4.
Update
`CodeGenerator`
to
support
target