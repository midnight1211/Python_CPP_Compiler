"""
Register Allocator for the code generator.
Implements register allocation using graph coloring or linear scan.
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import sys

sys.path.append('../..')

from src.ir.ir_instructions import *


@dataclass
class LiveRange:
    """Represents the live range of a variable."""
    variable: str
    start: int
    end: int
    uses: List[int] = field(default_factory=list)

    def overlaps(self, other: 'LiveRange') -> bool:
        """Check if this live range overlaps with another."""
        return not (self.end < other.start or other.end < self.start)


class RegisterAllocator:
    """
    Register allocator using linear scan algorithm.

    Assigns registers to temporaries and variables, spilling to
    stack when necessary.
    """

    def __init__(self, available_registers: List[str]):
        """
        Initialize register allocator.

        Args:
            available_registers: List of available register names
        """
        self.available_registers = available_registers
        self.allocation: Dict[str, str] = {}  # variable -> register/stack
        self.live_ranges: List[LiveRange] = []
        self.active: List[LiveRange] = []
        self.spill_count = 0

    def allocate(self, function: IRFunction) -> Dict[str, str]:
        """
        Allocate registers for a function.

        Args:
            function: IR function

        Returns:
            Mapping of variables to registers or stack locations
        """
        # Compute live ranges
        self.compute_live_ranges(function)

        # Sort by start point
        self.live_ranges.sort(key=lambda lr: lr.start)

        # Linear scan allocation
        self.allocation = {}
        self.active = []
        self.spill_count = 0

        for live_range in self.live_ranges:
            self.expire_old_intervals(live_range.start)

            if len(self.active) == len(self.available_registers):
                self.spill_at_interval(live_range)
            else:
                # Allocate register
                used_regs = {self.allocation[lr.variable]
                             for lr in self.active
                             if self.allocation[lr.variable] in self.available_registers}

                for reg in self.available_registers:
                    if reg not in used_regs:
                        self.allocation[live_range.variable] = reg
                        self.active.append(live_range)
                        self.active.sort(key=lambda lr: lr.end)
                        break

        return self.allocation

    def compute_live_ranges(self, function: IRFunction) -> None:
        """Compute live ranges for all variables."""
        self.live_ranges = []
        var_ranges: Dict[str, LiveRange] = {}

        # First pass: find first and last use of each variable
        for i, instr in enumerate(function.instructions):
            # Check all operands
            for value in [instr.result, instr.arg1, instr.arg2, instr.arg3]:
                if value and isinstance(value, (IRTemp, IRVariable)):
                    var_name = str(value)

                    if var_name not in var_ranges:
                        var_ranges[var_name] = LiveRange(var_name, i, i)
                    else:
                        var_ranges[var_name].end = i

                    var_ranges[var_name].uses.append(i)

        self.live_ranges = list(var_ranges.values())

    def expire_old_intervals(self, position: int) -> None:
        """Remove intervals that have expired."""
        self.active = [lr for lr in self.active if lr.end >= position]

    def spill_at_interval(self, live_range: LiveRange) -> None:
        """Spill a variable to stack."""
        # Find the interval with the furthest end point
        spill = max(self.active, key=lambda lr: lr.end)

        if spill.end > live_range.end:
            # Spill the furthest interval
            self.allocation[live_range.variable] = self.allocation[spill.variable]
            self.allocation[spill.variable] = self.get_spill_location()
            self.active.remove(spill)
            self.active.append(live_range)
            self.active.sort(key=lambda lr: lr.end)
        else:
            # Spill current interval
            self.allocation[live_range.variable] = self.get_spill_location()

    def get_spill_location(self) -> str:
        """Get a stack location for spilling."""
        self.spill_count += 1
        offset = self.spill_count * 8
        return f"[rbp-{offset}]"


class GraphColoringAllocator:
    """
    Register allocator using graph coloring.

    More sophisticated than linear scan, handles complex cases better.
    """

    def __init__(self, available_registers: List[str]):
        self.available_registers = available_registers
        self.interference_graph: Dict[str, Set[str]] = {}
        self.allocation: Dict[str, str] = {}
        self.colors = len(available_registers)

    def allocate(self, function: IRFunction) -> Dict[str, str]:
        """Allocate registers using graph coloring."""
        # Build interference graph
        self.build_interference_graph(function)

        # Color the graph
        self.color_graph()

        return self.allocation

    def build_interference_graph(self, function: IRFunction) -> None:
        """Build interference graph for variables."""
        # Compute live variables at each instruction
        live_vars = self.compute_liveness(function)

        # Build interference graph
        self.interference_graph = {}

        for i, instr in enumerate(function.instructions):
            live_at_i = live_vars[i]

            # All live variables at this point interfere with each other
            for var1 in live_at_i:
                if var1 not in self.interference_graph:
                    self.interference_graph[var1] = set()

                for var2 in live_at_i:
                    if var1 != var2:
                        self.interference_graph[var1].add(var2)

    def compute_liveness(self, function: IRFunction) -> List[Set[str]]:
        """Compute live variables at each instruction point."""
        n = len(function.instructions)
        live_in: List[Set[str]] = [set() for _ in range(n)]
        live_out: List[Set[str]] = [set() for _ in range(n)]

        # Iterative dataflow analysis
        changed = True
        while changed:
            changed = False

            for i in range(n - 1, -1, -1):
                instr = function.instructions[i]

                # Use and def sets
                use_vars = set()
                def_vars = set()

                if instr.arg1 and isinstance(instr.arg1, (IRTemp, IRVariable)):
                    use_vars.add(str(instr.arg1))
                if instr.arg2 and isinstance(instr.arg2, (IRTemp, IRVariable)):
                    use_vars.add(str(instr.arg2))
                if instr.arg3 and isinstance(instr.arg3, (IRTemp, IRVariable)):
                    use_vars.add(str(instr.arg3))

                if instr.result and isinstance(instr.result, (IRTemp, IRVariable)):
                    def_vars.add(str(instr.result))

                # live_in[i] = use[i] ∪ (live_out[i] - def[i])
                new_live_in = use_vars | (live_out[i] - def_vars)

                if new_live_in != live_in[i]:
                    live_in[i] = new_live_in
                    changed = True

                # live_out[i] = ∪ live_in[successor]
                # Simplified: assume next instruction is successor
                if i + 1 < n:
                    live_out[i] = live_in[i + 1].copy()

        return live_in

    def color_graph(self) -> None:
        """Color the interference graph."""
        self.allocation = {}

        # Greedy coloring
        for var in self.interference_graph:
            # Find colors used by neighbors
            used_colors = set()
            for neighbor in self.interference_graph[var]:
                if neighbor in self.allocation:
                    alloc = self.allocation[neighbor]
                    if alloc in self.available_registers:
                        used_colors.add(alloc)

            # Assign first available color
            for reg in self.available_registers:
                if reg not in used_colors:
                    self.allocation[var] = reg
                    break
            else:
                # Spill to stack
                self.allocation[var] = f"[stack_{var}]"


def allocate_registers(function: IRFunction,
                       available_registers: List[str],
                       algorithm: str = "linear") -> Dict[str, str]:
    """
    Convenience function to allocate registers.

    Args:
        function: IR function
        available_registers: List of available registers
        algorithm: "linear" or "graph"

    Returns:
        Variable to location mapping
    """
    if algorithm == "linear":
        allocator = RegisterAllocator(available_registers)
    elif algorithm == "graph":
        allocator = GraphColoringAllocator(available_registers)
    else:
        raise ValueError(f"Unknown allocation algorithm: {algorithm}")

    return allocator.allocate(function)