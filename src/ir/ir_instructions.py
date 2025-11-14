"""
Intermediate Representation (IR) instruction definitions.
Defines a three-address code instruction set for the compiler.
"""

from dataclasses import dataclass
from typing import Optional, List, Any
from enum import Enum, auto


class IROpcode(Enum):
    """IR instruction opcodes."""

    # Arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    NEG = auto()

    # Bitwise
    AND = auto()
    OR = auto()
    XOR = auto()
    NOT = auto()
    SHL = auto()
    SHR = auto()

    # Logical
    LAND = auto()
    LOR = auto()
    LNOT = auto()

    # Comparison
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    # Memory
    LOAD = auto()
    STORE = auto()
    LOAD_ADDR = auto()
    ALLOC = auto()
    FREE = auto()

    # Assignment
    ASSIGN = auto()

    # Control Flow
    LABEL = auto()
    GOTO = auto()
    IF_FALSE = auto()
    IF_TRUE = auto()

    # Function calls
    PARAM = auto()
    CALL = auto()
    RETURN = auto()

    # Array/Pointer operations
    INDEX = auto()
    STORE_INDEX = auto()

    # Type conversions
    CAST = auto()

    # Special
    NOP = auto()
    PHI = auto()


@dataclass
class IRValue:
    """Base class for IR values."""
    pass

@dataclass
class IRTemp(IRValue):
    """Temporary variable (like t1, t2, etc.)."""
    name: str

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"IRTemp({self.name})"

@dataclass
class IRConstant(IRValue):
    """Constant value."""
    value: Any

    def __str__(self):
        if isinstance(self.value, str):
            return f'"{self.value}"'
        return str(self.value)

    def __repr__(self):
        return f"IRConstant({self.value})"

@dataclass
class IRVariable(IRValue):
    """Named variable."""
    name: str

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"IRVariable({self.name})"

@dataclass
class IRLabel(IRValue):
    """Label for control flow."""
    name: str

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"IRLabel({self.name})"

@dataclass
class IRInstruction:
    """
    Three=address code instruction

    General form:  result = arg1 op arg2
    """
    opcode: IROpcode
    result: Optional[IRValue] = None
    arg1: Optional[IRValue] = None
    arg2: Optional[IRValue] = None
    arg3: Optional[IRValue] = None
    lavel: Optional[IRLabel] = None

    def __str__(self):
        """String representation of the instruction."""
        if self.opcode == IROpcode.LABEL:
            return f"{self.label}"

        if self.opcode == IROpcode.GOTO:
            return f"    goto {self.label}"

        if self.opcode == IROpcode.IF_FALSE:
            return f"    if !{self.arg1} goto {self.label}"

        if self.opcode == IROpcode.IF_TRUE:
            return f"    if {self.arg1} goto {self.label}"

        if self.opcode == IROpcode.PARAM:
            return f"    param {self.arg1}"

        if self.opcode == IROpcode.CALL:
            if self.result:
                return f"    {self.result} = call {self.arg1}({self.arg2})"
            return f"    call {self.arg1}({self.arg2})"

        if self.opcode == IROpcode.RETURN:
            if self.arg1:
                return f"    return {self.arg1}"
            return f"    return"

        if self.opcode == IROpcode.ALLOC:
            return f"    {self.result} = alloc {self.arg1}"

        if self.opcode == IROpcode.FREE:
            return f"    free {self.arg1}"

        if self.opcode == IROpcode.LOAD:
            return f"    {self.result} = *{self.arg1}"

        if self.opcode == IROpcode.STORE:
            return f"    *{self.result} = {self.arg1}"

        if self.opcode == IROpcode.LOAD_ADDR:
            return f"    {self.result} = &{self.arg1}"

        if self.opcode == IROpcode.INDEX:
            return f"    {self.result} = {self.arg1}[{self.arg2}]"

        if self.opcode == IROpcode.STORE_INDEX:
            return f"    {self.arg1}[{self.arg2}] = {self.arg3}"

        if self.opcode == IROpcode.CAST:
            return f"    {self.result} = cast {self.arg1}"

        if self.opcode == IROpcode.NOP:
            return f"    nop"

            # Binary operations
        if self.arg2 is not None:
            op_symbols = {
                IROpcode.ADD: '+',
                IROpcode.SUB: '-',
                IROpcode.MUL: '*',
                IROpcode.DIV: '/',
                IROpcode.MOD: '%',
                IROpcode.AND: '&',
                IROpcode.OR: '|',
                IROpcode.XOR: '^',
                IROpcode.SHL: '<<',
                IROpcode.SHR: '>>',
                IROpcode.LAND: '&&',
                IROpcode.LOR: '||',
                IROpcode.EQ: '==',
                IROpcode.NE: '!=',
                IROpcode.LT: '<',
                IROpcode.LE: '<=',
                IROpcode.GT: '>',
                IROpcode.GE: '>=',
            }
            op = op_symbols.get(self.opcode, self.opcode.name.lower())
            return f"    {self.result} = {self.arg1} {op} {self.arg2}"

            # Unary operations
        if self.arg1 is not None:
            if self.opcode == IROpcode.ASSIGN:
                return f"    {self.result} = {self.arg1}"

            unary_ops = {
                IROpcode.NEG: '-',
                IROpcode.NOT: '~',
                IROpcode.LNOT: '!',
            }
            op = unary_ops.get(self.opcode, self.opcode.name.lower())
            return f"    {self.result} = {op}{self.arg1}"

        return f"    {self.opcode.name}"

    def __repr__(self):
        return self.__str__()

@dataclass
class IRFunction:
    """
    IR representation of a function.

    Contains the function's instructions and metadata.
    """
    name: str
    parameters: List[IRVariable]
    return_type: Any
    instructions: List[IRInstruction]
    loval_vars: List[IRVariable]

    def __str__(self):
        """String representation of the function."""
        lines = [f"function {self.name}({', '.join(str(p) for p in self.parameters)}):"]

        if self.local_vars:
            lines.append(f"    # Local variables: {', '.join(str(v) for v in self.local_vars)}")

        for instr in self.instructions:
            lines.append(str(instr))

        return '\n'.join(lines)

@dataclass
class IRProgram:
    """
    Complete IR program.

    Contains all functions and global data.
    """
    functions: List[IRFunction]
    global_vars: List[IRVariable]
    string_literals: List[tuple[str, str]]

    def __str__(self):
        """String representation of the program."""
        lines = []

        # Global variables
        if self.global_vars:
            lines.append("# Global variables:")
            for var in self.global_vars:
                lines.append(f"global {var}")
            lines.append("")

        # String literals
        if self.string_literals:
            lines.append("# String literals:")
            for label, value in self.string_literals:
                lines.append(f'{label}: "{value}"')
            lines.append("")

        # Functions
        for func in self.functions:
            lines.append(str(func))
            lines.append("")

        return '\n'.join(lines)

class IRBuilder:
    """
    Helper class for building IR code.

    Provides convenient methods for generating IR instructions.
    """

    def __init__(self):
        self.instructions: List[IRInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self) -> IRTemp:
        """"Generate a new temporary variable."""
        temp = IRTemp(f"t{self.temp_counter}")
        self.temp_counter += 1
        return temp

    def new_label(self, prefix: str = "L") -> IRLabel:
        """Generate a new label."""
        label = IRLabel(f"{prefix}{self.label_counter}")
        self.label_counter += 1
        return label

    def emit(self, instruction: IRInstruction) -> None:
        """"Emit an instruction."""
        self.instructions.append(instruction)

    def emit_binary(self, opcode: IROpcode, result: IRValue, arg1: IRValue, arg2: IRValue) -> None:
        """Emit a binary operation."""
        self.emit(IRInstruction(opcode, result, arg1, arg2))

    def emit_unary(self, opcode: IROpcode, result: IRValue, arg1: IRValue) -> None:
        """Emit a unary operation."""
        self.emit(IRInstruction(opcode, result, arg1))

    def emit_assign(self, result: IRValue, arg1: IRValue) -> None:
        """Emit an assignment."""
        self.emit(IRInstruction(IROpcode.ASSIGN, result, arg1))

    def emit_label(self, label: IRLabel) -> None:
        """Emit a label."""
        self.emit(IRInstruction(IROpcode.LABEL, label=label))

    def emit_goto(self, label: IRLabel) -> None:
        """Emit an unconditional jump."""
        self.emit(IRInstruction(IROpcode.GOTO, label=label))

    def emit_if_false(self, condition: IRValue, label: IRLabel) -> None:
        """Emit a conditional jump (if false)."""
        self.emit(IRInstruction(IROpcode.IF_FALSE, arg1=condition, label=label))

    def emit_if_true(self, condition: IRValue, label: IRLabel) -> None:
        """Emit a conditional jump (if true)."""
        self.emit(IRInstruction(IROpcode.IF_TRUE, arg1=condition, label=label))

    def emit_param(self, arg: IRValue) -> None:
        """Emit a parameter push."""
        self.emit(IRInstruction(IROpcode.PARAM, arg1=arg))

    def emit_call(self, result: Optional[IRValue], function: IRValue,
                  num_args: int) -> None:
        """Emit a function call."""
        self.emit(IRInstruction(
            IROpcode.CALL,
            result=result,
            arg1=function,
            arg2=IRConstant(num_args)
        ))

    def emit_return(self, value: Optional[IRValue] = None) -> None:
        """Emit a return statement."""
        self.emit(IRInstruction(IROpcode.RETURN, arg1=value))

    def emit_load(self, result: IRValue, address: IRValue) -> None:
        """Emit a memory load."""
        self.emit(IRInstruction(IROpcode.LOAD, result, address))

    def emit_store(self, address: IRValue, value: IRValue) -> None:
        """Emit a memory store."""
        self.emit(IRInstruction(IROpcode.STORE, address, value))

    def emit_load_addr(self, result: IRValue, var: IRValue) -> None:
        """Emit address-of operation."""
        self.emit(IRInstruction(IROpcode.LOAD_ADDR, result, var))

    def emit_alloc(self, result: IRValue, size: IRValue) -> None:
        """Emit memory allocation."""
        self.emit(IRInstruction(IROpcode.ALLOC, result, size))

    def emit_free(self, pointer: IRValue) -> None:
        """Emit memory deallocation."""
        self.emit(IRInstruction(IROpcode.FREE, arg1=pointer))

    def emit_index(self, result: IRValue, array: IRValue,
                   index: IRValue) -> None:
        """Emit array indexing."""
        self.emit(IRInstruction(IROpcode.INDEX, result, array, index))

    def emit_store_index(self, array: IRValue, index: IRValue,
                        value: IRValue) -> None:
        """Emit array store."""
        self.emit(IRInstruction(
            IROpcode.STORE_INDEX,
            arg1=array,
            arg2=index,
            arg3=value
        ))