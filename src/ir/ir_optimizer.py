"""
IR Optimizer for the C++ compiler.
Performs optimization passes on the intermediate representation.
"""

from typing import Dict, Set
from .ir_instructions import *

class IROptimizer:
    """
    IR Optimizer that performs various optimization passes.

    Optimizations include:
    - Constant folding
    - Constant propagation
    - Dead code elimination
    - Copy propagation
    - Common subexpression elimination
    """

    def __init__(self):
        self.changed = False

    def optimize(self, program: IRProgram, passes: int = 3) -> IRProgram:
        """
        Optimize an IR program.

        Args:
            program: IR program to optimize.
            passes: Number of optimization passes

        Returns:
            Optimized IR program.
        """
        for i in range(passes):
            self.changed = False

            # Optimize each function
            for func in program.function:
                self.optimize_function(func)

            # Stop if no changes made
            if not self.changed:
                break

        return program

    def optimize_function(self, function: IRFunction) -> None:
        """Optimize a single function."""
        # Run optimization passes
        self.constant_folding(function)
        self.constant_propagation(function)
        self.copy_propagation(function)
        self.dead_code_elimination(function)
        self.remove_nops(function)

    def constant_folding(self, function: IRFunction) -> None:
        """
        Constant folding optimization.

        Evaluates constant expressions at compile time.
        Example: t1 = 2 + 3 -> t1 = 5
        """
        for i, instr in enumerate(function.instructions):
            if not self.is_binary_arithmetic(instr):
                continue
            # Check if both operands are constants
            if not isinstance(instr.arg1, IRConstant) or not isinstance(instr.arg2, IRConstant):
                continue

            # Evaluate the operation
            result = self.evaluate_binary_op(instr.opcode, instr.arg1.value, instr.arg2.value)

            if result is not None:
                #Replace with assignment
                function.instructions[i] = IRInstruction(
                    IROpcode.ASSIGN,
                    instr.result,
                    IRConstant(result)
                )
                self.changed = True

    def constant_propagation(self, function: IRFunction) -> None:
        """
        Constant propagation optimization.

        Replaces uses of variables with their constant values.
        Example: x = 5; y = x --> x = 5; y = 5
        """
        const_map: Dict[str, Any] = {}

        for i, instr in enumerate(function.instructions):
            # Track constant assignments
            if instr.opcode == IROpcode.ASSIGN:
                if isinstance(instr.result, (IRTemp, IRVariable)) and isinstance(instr.arg1, IRConstant):
                    const_map[str(instr.result)] = instr.arg1.value

            # Replace uses with constants
            if instr.arg1 and isinstance(instr.arg1, (IRTemp, IRVariable)):
                if str(instr.arg1) in const_map:
                    instr.arg1 = IRConstant(const_map[str(instr.arg1)])
                    self.changed = True

                if instr.arg2 and isinstance(instr.arg2, (IRTemp, IRVariable)):
                    if str(instr.arg2) in const_map:
                        instr.arg2 = IRConstant(const_map[str(instr.arg2)])
                        self.changed = True

                if instr.result and isinstance(instr.result, (IRTemp, IRVariable)):
                    if str(instr.result) in const_map:
                        del const_map[str(instr.result)]

    def copy_propagation(self, function: IRFunction) -> None:
        """
        Copy propagation optimization.

        Replaces uses of variables with their copied values.
        Example: x = y; z = x --> x = y; z = y
        """
        copy_map: Dict[str, IRValue] = {}

        for i, instr in enumerate(function.instructions):
            # Track simple copies
            if instr.opcode == IROpcode.ASSIGN:
                if isinstance(instr.result, (IRTemp, IRVariable)) and isinstance(instr.arg1, (IRTemp, IRVariable)):
                    copy_map[str(instr.result)] = instr.arg1

            # Replace uses with copied values
            if instr.arg1 and isinstance(instr.arg1, (IRTemp, IRVariable)):
                if str(instr.arg1) in copy_map:
                    instr.arg1 = copy_map[str(instr.arg1)]
                    self.changed = True

            if instr.arg2 and isinstance(instr.arg2, (IRTemp, IRVariable)):
                if str(instr.arg2) in copy_map:
                    instr.arg2 = copy_map[str(instr.arg2)]
                    self.changed = True

            # Clear copy map if variable is reassigned
            if instr.result and isinstance(instr.result, (IRTemp, IRVariable)):
                if str(instr.result) in copy_map:
                    del copy_map[str(instr.result)]

    def dead_code_elimination(self, function: IRFunction) -> None:
        """
        Dead code elimination.

        Removes instructions whose results are never used.
        """
        # Find all used values
        used: Set[str] = set()

        for instr in function.instructions:
            # Mark arguments as used
            if instr.arg1 and isinstance(instr.arg1, (IRTemp, IRVariable)):
                used.add(str(instr.arg1))
            if instr.arg2 and isinstance(instr.arg2, (IRTemp, IRVariable)):
                used.add(str(instr.arg2))
            if instr.arg3 and isinstance(instr.arg3, (IRTemp, IRVariable)):
                used.add(str(instr.arg3))

            # Always keep: returns, calls, stores, control flow
            if instr.opcode in [IROpcode.RETURN, IROpcode.CALL, IROpcode.STORE,
                                IROpcode.STORE_INDEX, IROpcode.GOTO,
                                IROpcode.IF_FALSE, IROpcode.IF_TRUE,
                                IROpcode.LABEL, IROpcode.PARAM, IROpcode.FREE]:
                # These have side effects, mark as essential
                pass

        # Remove instructions with unused results
        new_instructions = []
        for instr in function.instructions:
            # Keep if no result or result is used
            if not instr.result or str(instr.result) in used or instr.opcode in [IROpcode.RETURN, IROpcode.CALL, IROpcode.STORE,
                                                                                IROpcode.STORE_INDEX, IROpcode.GOTO,
                                                                                IROpcode.IF_FALSE, IROpcode.IF_TRUE,
                                                                                IROpcode.LABEL, IROpcode.PARAM, IROpcode.FREE]:
                new_instructions.append(instr)
            else:
                self.changed = True

            function.instructions = new_instructions

    def remove_nops(self, function: IRFunction) -> None:
        """Remove NOP instructions."""
        new_instructions = []

        for instr in function.instructions:
            if instr.opcode != IROpcode.NOP:
                new_instructions.append(instr)
            else:
                self.changed = True

        function.instructions = new_instructions

    def is_binary_arithmetic(self, instr: IRInstruction) -> bool:
        """Check if instruction is a binary arithmetic operation."""
        return instr.opcode in [
            IROpcode.ADD, IROpcode.SUB, IROpcode.MUL, IROpcode.DIV, IROpcode.MOD,
            IROpcode.AND, IROpcode.OR, IROpcode.XOR, IROpcode.SHL, IROpcode.SHR,
            IROpcode.LAND, IROpcode.LOR,
            IROpcode.EQ, IROpcode.NE, IROpcode.LT, IROpcode.LE, IROpcode.GT, IROpcode.GE
        ]

    def evaluate_binary_op(self, opcode: IROpcode, left: Any, right: Any) -> Optional[Any]:
        """Evaluate a binary operation on constants."""
        try:
            if opcode == IROpcode.ADD:
                return left + right
            elif opcode == IROpcode.SUB:
                return left - right
            elif opcode == IROpcode.MUL:
                return left * right
            elif opcode == IROpcode.DIV:
                if right == 0:
                    return None  # Avoid division by zero
                return left // right if isinstance(left, int) else left / right
            elif opcode == IROpcode.MOD:
                if right == 0:
                    return None
                return left % right
            elif opcode == IROpcode.AND:
                return left & right
            elif opcode == IROpcode.OR:
                return left | right
            elif opcode == IROpcode.XOR:
                return left ^ right
            elif opcode == IROpcode.SHL:
                return left << right
            elif opcode == IROpcode.SHR:
                return left >> right
            elif opcode == IROpcode.LAND:
                return 1 if (left and right) else 0
            elif opcode == IROpcode.LOR:
                return 1 if (left or right) else 0
            elif opcode == IROpcode.EQ:
                return 1 if left == right else 0
            elif opcode == IROpcode.NE:
                return 1 if left != right else 0
            elif opcode == IROpcode.LT:
                return 1 if left < right else 0
            elif opcode == IROpcode.LE:
                return 1 if left <= right else 0
            elif opcode == IROpcode.GT:
                return 1 if left > right else 0
            elif opcode == IROpcode.GE:
                return 1 if left >= right else 0
        except:
            return None

        return None

class PeepholeOptimizer:
    """
    Peephole optimizer.

    Performs local optimizations on small windows of instructions.
    """

    def __init__(self):
        self.window_size = 3

    def optimize(self, function: IRFunction) -> None:
        """Apply peephole optimizations."""
        self.remove_redundant_loads_stores(function)
        self.simplify_arithmetic(function)

    def remove_redundant_loads_stores(self, function: IRFunction) -> None:
        """
        Remove redundant load/store pairs.

        Example:
        x = y
        z = x
        --> z = y
        """
        i = 0
        while i < len(function.instructions) - 1:
            instr1 = function.instructions[i]
            instr2 = function.instructions[i + 1]

            # x = y; z = x --> z = y
            if instr1.opcode == IROpcode.ASSIGN and instr2.opcode == IROpcode.ASSIGN:
                if instr2.arg1 == instr1.result:
                    instr2.arg1 = instr1.arg1

            i += 1

    def simplify_arithmetic(self, function: IRFunction) -> None:
        """
        Simplify arithmetic operations.

        Examples:
        - x = y + 0 --> x = y
        - x = y * 1 --> x = y
        - x = y * 0 --> x = 0
        """
        for i, instr in enumerate(function.instructions):
            if instr.opcode == IROpcode.ADD:
                # x = y + 0 --> x = y
                if isinstance(instr.arg2, IRConstant) and instr.arg2.value == 0:
                    function.instructions[i] = IRInstruction(IROpcode.ASSIGN, instr.result, instr.arg1)
                elif isinstance(instr.arg1, IRConstant) and instr.arg1.value == 0:
                    function.instructions[i] = IRConstant(IROpcode.ASSIGN, instr.result, instr.arg2)
            elif instr.opcode == IROpcode.MUL:
                # x = y * 0 --> x = 0
                if isinstance(instr.arg2, IRConstant) and instr.arg2.value == 0:
                    function.instructions[i] = IRInstruction(IROpcode.ASSIGN, instr.result, IRConstant(0))
                elif isinstance(instr.arg1, IRConstant) and instr.arg1.value == 0:
                    function.instructions[i] = IRInstruction(IROpcode.ASSIGN, instr.result, IRConstant(0))
                # x = y * 1 --> x = y
                elif isinstance(instr.arg2, IRConstant) and instr.arg2.value == 1:
                    function.instruction[i] = IRInstruction(IROpcode.ASSIGN, instr.result, instr.arg1)
                elif isinstance(instr.arg1, IRConstant) and instr.arg1.value == 1:
                    function.instructions[i] = IRInstruction(IROpcode.ASSIGN, instr.result, instr.arg2)


def optimize_ir(program: IRProgram, level: int = 2) -> IRProgram:
    """
    Convenience function to optimize IR program.

    Args:
        program: IR program to optimize
        level: Optimization level (0-3)

    Returns:
        Optimized IR program
    """
    if level == 0:
        return program

    optimizer = IROptimizer()
    program = optimizer.optimize(program, passes=level)

    if level >= 2:
        peephole = PeepholeOptimizer()
        for func in program.functions:
            peephole.optimize(func)

    return program