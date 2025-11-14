"""
IR Generator for the C++ compiler.
Converts AST to intermediate representation (three-address code).
"""

from typing import Optional, List, Dict, Any
import sys
sys.path.append('../..')

from src.parser.ast_nodes import *
from .ir_instructions import *


class IRGeneratorError(Exception):
    """Exception raised for IR generation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"IR generation error: {message}")


class IRGenerator:
    """
    IR Generator using the Visitor pattern.

    Traverses the AST and generates three-address code instructions.
    """

    def __init__(self):
        self.builder = IRBuilder()
        self.functions: List[IRFunction] = []
        self.global_vars: List[IRVariable] = []
        self.string_literals: List[tuple[str, str]] = []
        self.string_counter = 0

        # Symbol tables
        self.var_map: Dict[str, IRValue] = {}  # AST name -> IR value
        self.current_function: Optional[str] = None
        self.local_vars: List[IRVariable] = []

        # Control flow
        self.break_labels: List[IRLabel] = []
        self.continue_labels: List[IRLabel] = []

    def generate(self, program: Program) -> IRProgram:
        """
        Generate IR for a program.

        Args:
            program: Program AST node

        Returns:
            IRProgram with all generated code
        """
        for declaration in program.declarations:
            declaration.accept(self)

        return IRProgram(self.functions, self.global_vars, self.string_literals)

    # Visitor methods for Declarations
    def visit_variable_declaration(self, node: VariableDeclaration) -> IRValue:
        """Visit variable declaration."""
        var = IRVariable(node.name)

        if self.current_function is None:
            # Global variable
            self.global_vars.append(var)
        else:
            # Local variable
            self.local_vars.append(var)

        self.var_map[node.name] = var

        # Handle initializer
        if node.initializer:
            init_value = node.initializer.accept(self)
            self.builder.emit_assign(var, init_value)

        return var

    def visit_function_declaration(self, node: FunctionDeclaration) -> None:
        """Visit function declaration."""
        if node.body is None:
            return  # Function declaration without body

        self.current_function = node.name
        self.local_vars = []
        self.builder.clear()

        # Create parameter IR variables
        params = []
        for param in node.parameters:
            param_var = IRVariable(param.name)
            params.append(param_var)
            self.var_map[param.name] = param_var

        # Generate function body
        node.body.accept(self)

        # Ensure function ends with return
        last_instr = self.builder.instructions[-1] if self.builder.instructions else None
        if not last_instr or last_instr.opcode != IROpcode.RETURN:
            self.builder.emit_return(None)

        # Create function
        function = IRFunction(
            name=node.name,
            parameters=params,
            return_type=node.return_type,
            instructions=self.builder.get_instructions(),
            local_vars=self.local_vars
        )

        self.functions.append(function)
        self.current_function = None

    def visit_class_declaration(self, node: ClassDeclaration) -> None:
        """Visit class declaration."""
        # For now, just process methods
        for member in node.members:
            if isinstance(member, FunctionDeclaration):
                member.accept(self)
            elif isinstance(member, ConstructorDeclaration):
                member.accept(self)
            elif isinstance(member, DestructorDeclaration):
                member.accept(self)

    def visit_constructor_declaration(self, node: ConstructorDeclaration) -> None:
        """Visit constructor."""
        self.current_function = f"{node.class_name}::constructor"
        self.local_vars = []
        self.builder.clear()

        # Parameters
        params = []
        for param in node.parameters:
            param_var = IRVariable(param.name)
            params.append(param_var)
            self.var_map[param.name] = param_var

        # Initializer list
        for init in node.initializer_list:
            init.accept(self)

        # Body
        if node.body:
            node.body.accept(self)

        self.builder.emit_return(None)

        function = IRFunction(
            name=self.current_function,
            parameters=params,
            return_type=None,
            instructions=self.builder.get_instructions(),
            local_vars=self.local_vars
        )

        self.functions.append(function)
        self.current_function = None

    def visit_destructor_declaration(self, node: DestructorDeclaration) -> None:
        """Visit destructor."""
        self.current_function = f"{node.class_name}::destructor"
        self.local_vars = []
        self.builder.clear()

        if node.body:
            node.body.accept(self)

        self.builder.emit_return(None)

        function = IRFunction(
            name=self.current_function,
            parameters=[],
            return_type=None,
            instructions=self.builder.get_instructions(),
            local_vars=self.local_vars
        )

        self.functions.append(function)
        self.current_function = None

    def visit_member_initializer(self, node: MemberInitializer) -> None:
        """Visit member initializer."""
        # Generate: this->member = value
        value = node.value.accept(self)
        member_var = IRVariable(node.member_name)
        self.builder.emit_assign(member_var, value)

    def visit_namespace_declaration(self, node: NamespaceDeclaration) -> None:
        """Visit namespace."""
        for declaration in node.declarations:
            declaration.accept(self)

    # Visitor methods for Statements
    def visit_compound_statement(self, node: CompoundStatement) -> None:
        """Visit compound statement."""
        for statement in node.statements:
            statement.accept(self)

    def visit_expression_statement(self, node: ExpressionStatement) -> None:
        """Visit expression statement."""
        node.expression.accept(self)

    def visit_return_statement(self, node: ReturnStatement) -> None:
        """Visit return statement."""
        if node.value:
            return_value = node.value.accept(self)
            self.builder.emit_return(return_value)
        else:
            self.builder.emit_return(None)

    def visit_if_statement(self, node: IfStatement) -> None:
        """Visit if statement."""
        # Generate condition
        condition = node.condition.accept(self)

        # Create labels
        else_label = self.builder.new_label("else")
        end_label = self.builder.new_label("endif")

        # if (!condition) goto else_label
        self.builder.emit_if_false(condition, else_label)

        # Then branch
        node.then_statement.accept(self)
        self.builder.emit_goto(end_label)

        # Else branch
        self.builder.emit_label(else_label)
        if node.else_statement:
            node.else_statement.accept(self)

        # End
        self.builder.emit_label(end_label)

    def visit_while_statement(self, node: WhileStatement) -> None:
        """Visit while statement."""
        start_label = self.builder.new_label("while_start")
        end_label = self.builder.new_label("while_end")

        # Track labels for break/continue
        self.break_labels.append(end_label)
        self.continue_labels.append(start_label)

        # Loop start
        self.builder.emit_label(start_label)

        # Condition
        condition = node.condition.accept(self)
        self.builder.emit_if_false(condition, end_label)

        # Body
        node.body.accept(self)

        # Loop back
        self.builder.emit_goto(start_label)

        # Loop end
        self.builder.emit_label(end_label)

        self.break_labels.pop()
        self.continue_labels.pop()

    def visit_do_while_statement(self, node: DoWhileStatement) -> None:
        """Visit do-while statement."""
        start_label = self.builder.new_label("do_start")
        end_label = self.builder.new_label("do_end")

        self.break_labels.append(end_label)
        self.continue_labels.append(start_label)

        # Loop start
        self.builder.emit_label(start_label)

        # Body
        node.body.accept(self)

        # Condition
        condition = node.condition.accept(self)
        self.builder.emit_if_true(condition, start_label)

        # Loop end
        self.builder.emit_label(end_label)

        self.break_labels.pop()
        self.continue_labels.pop()

    def visit_for_statement(self, node: ForStatement) -> None:
        """Visit for statement."""
        start_label = self.builder.new_label("for_start")
        increment_label = self.builder.new_label("for_incr")
        end_label = self.builder.new_label("for_end")

        self.break_labels.append(end_label)
        self.continue_labels.append(increment_label)

        # Initialization
        if node.init:
            node.init.accept(self)

        # Loop start
        self.builder.emit_label(start_label)

        # Condition
        if node.condition:
            condition = node.condition.accept(self)
            self.builder.emit_if_false(condition, end_label)

        # Body
        node.body.accept(self)

        # Increment
        self.builder.emit_label(increment_label)
        if node.increment:
            node.increment.accept(self)

        # Loop back
        self.builder.emit_goto(start_label)

        # Loop end
        self.builder.emit_label(end_label)

        self.break_labels.pop()
        self.continue_labels.pop()

    def visit_break_statement(self, node: BreakStatement) -> None:
        """Visit break statement."""
        if self.break_labels:
            self.builder.emit_goto(self.break_labels[-1])

    def visit_continue_statement(self, node: ContinueStatement) -> None:
        """Visit continue statement."""
        if self.continue_labels:
            self.builder.emit_goto(self.continue_labels[-1])

    def visit_switch_statement(self, node: SwitchStatement) -> None:
        """Visit switch statement."""
        # Evaluate switch expression
        switch_value = node.condition.accept(self)

        end_label = self.builder.new_label("switch_end")
        self.break_labels.append(end_label)

        # Create labels for each case
        case_labels = []
        default_label = None

        for case in node.cases:
            if case.value is None:  # default case
                default_label = self.builder.new_label("default")
            else:
                case_labels.append(self.builder.new_label("case"))

        # Generate case comparisons
        case_idx = 0
        for i, case in enumerate(node.cases):
            if case.value is not None:
                # Compare switch_value with case value
                case_value = case.value.accept(self)
                temp = self.builder.new_temp()
                self.builder.emit_binary(IROpcode.EQ, temp, switch_value, case_value)
                self.builder.emit_if_true(temp, case_labels[case_idx])
                case_idx += 1

        # If no match, go to default or end
        if default_label:
            self.builder.emit_goto(default_label)
        else:
            self.builder.emit_goto(end_label)

        # Generate case bodies
        case_idx = 0
        for case in node.cases:
            if case.value is None:
                self.builder.emit_label(default_label)
            else:
                self.builder.emit_label(case_labels[case_idx])
                case_idx += 1

            for statement in case.statements:
                statement.accept(self)

        # End
        self.builder.emit_label(end_label)
        self.break_labels.pop()

    # Visitor methods for Expressions
    def visit_integer_literal(self, node: IntegerLiteral) -> IRValue:
        """Visit integer literal."""
        return IRConstant(node.value)

    def visit_float_literal(self, node: FloatLiteral) -> IRValue:
        """Visit float literal."""
        return IRConstant(node.value)

    def visit_char_literal(self, node: CharLiteral) -> IRValue:
        """Visit char literal."""
        return IRConstant(ord(node.value[1]))  # Convert 'a' to 97

    def visit_string_literal(self, node: StringLiteral) -> IRValue:
        """Visit string literal."""
        # Create a label for the string
        label = f"str{self.string_counter}"
        self.string_counter += 1

        # Store the string
        self.string_literals.append((label, node.value))

        # Return the label as a value
        return IRLabel(label)

    def visit_bool_literal(self, node: BoolLiteral) -> IRValue:
        """Visit bool literal."""
        return IRConstant(1 if node.value else 0)

    def visit_nullptr_literal(self, node: NullptrLiteral) -> IRValue:
        """Visit nullptr literal."""
        return IRConstant(0)

    def visit_identifier(self, node: Identifier) -> IRValue:
        """Visit identifier."""
        if node.name in self.var_map:
            return self.var_map[node.name]

        # Create new variable if not found
        var = IRVariable(node.name)
        self.var_map[node.name] = var
        return var

    def visit_binary_expression(self, node: BinaryExpression) -> IRValue:
        """Visit binary expression."""
        left = node.left.accept(self)
        right = node.right.accept(self)

        # Map operators to opcodes
        op_map = {
            '+': IROpcode.ADD,
            '-': IROpcode.SUB,
            '*': IROpcode.MUL,
            '/': IROpcode.DIV,
            '%': IROpcode.MOD,
            '&': IROpcode.AND,
            '|': IROpcode.OR,
            '^': IROpcode.XOR,
            '<<': IROpcode.SHL,
            '>>': IROpcode.SHR,
            '&&': IROpcode.LAND,
            '||': IROpcode.LOR,
            '==': IROpcode.EQ,
            '!=': IROpcode.NE,
            '<': IROpcode.LT,
            '<=': IROpcode.LE,
            '>': IROpcode.GT,
            '>=': IROpcode.GE,
        }

        opcode = op_map.get(node.operator)
        if opcode:
            result = self.builder.new_temp()
            self.builder.emit_binary(opcode, result, left, right)
            return result

        raise IRGeneratorError(f"Unsupported binary operator: {node.operator}")

    def visit_unary_expression(self, node: UnaryExpression) -> IRValue:
        """Visit unary expression."""
        operand = node.operand.accept(self)

        # Map operators to opcodes
        op_map = {
            '-': IROpcode.NEG,
            '~': IROpcode.NOT,
            '!': IROpcode.LNOT,
        }

        if node.operator in op_map:
            result = self.builder.new_temp()
            self.builder.emit_unary(op_map[node.operator], result, operand)
            return result

        # Handle increment/decrement
        if node.operator in ['++', '--']:
            one = IRConstant(1)
            result = self.builder.new_temp()

            if node.operator == '++':
                self.builder.emit_binary(IROpcode.ADD, result, operand, one)
            else:
                self.builder.emit_binary(IROpcode.SUB, result, operand, one)

            # Store back to operand
            self.builder.emit_assign(operand, result)

            # Return appropriate value based on prefix/postfix
            if node.is_postfix:
                return operand  # Return old value
            else:
                return result  # Return new value

        # Address-of
        if node.operator == '&':
            result = self.builder.new_temp()
            self.builder.emit_load_addr(result, operand)
            return result

        # Dereference
        if node.operator == '*':
            result = self.builder.new_temp()
            self.builder.emit_load(result, operand)
            return result

        raise IRGeneratorError(f"Unsupported unary operator: {node.operator}")

    def visit_assignment_expression(self, node: AssignmentExpression) -> IRValue:
        """Visit assignment expression."""
        value = node.value.accept(self)
        target = node.target.accept(self)

        if node.operator == '=':
            self.builder.emit_assign(target, value)
        else:
            # Compound assignment: x += y -> x = x + y
            op_map = {
                '+=': IROpcode.ADD,
                '-=': IROpcode.SUB,
                '*=': IROpcode.MUL,
                '/=': IROpcode.DIV,
                '%=': IROpcode.MOD,
                '&=': IROpcode.AND,
                '|=': IROpcode.OR,
                '^=': IROpcode.XOR,
                '<<=': IROpcode.SHL,
                '>>=': IROpcode.SHR,
            }

            opcode = op_map.get(node.operator)
            if opcode:
                temp = self.builder.new_temp()
                self.builder.emit_binary(opcode, temp, target, value)
                self.builder.emit_assign(target, temp)
            else:
                raise IRGeneratorError(f"Unsupported assignment operator: {node.operator}")

        return target

    def visit_call_expression(self, node: CallExpression) -> IRValue:
        """Visit call expression."""
        # Push parameters
        for arg in node.arguments:
            arg_value = arg.accept(self)
            self.builder.emit_param(arg_value)

        # Get function name
        if isinstance(node.function, Identifier):
            func_name = IRVariable(node.function.name)
        else:
            func_name = node.function.accept(self)

        # Call
        result = self.builder.new_temp()
        self.builder.emit_call(result, func_name, len(node.arguments))

        return result

    def visit_array_access_expression(self, node: ArrayAccessExpression) -> IRValue:
        """Visit array access."""
        array = node.array.accept(self)
        index = node.index.accept(self)

        result = self.builder.new_temp()
        self.builder.emit_index(result, array, index)

        return result

    def visit_member_access_expression(self, node: MemberAccessExpression) -> IRValue:
        """Visit member access."""
        obj = node.object.accept(self)

        # For simplicity, treat as variable access
        # Full implementation would need struct offsets
        member = IRVariable(f"{obj}.{node.member}")
        return member

    def visit_ternary_expression(self, node: TernaryExpression) -> IRValue:
        """Visit ternary expression."""
        condition = node.condition.accept(self)

        true_label = self.builder.new_label("ternary_true")
        false_label = self.builder.new_label("ternary_false")
        end_label = self.builder.new_label("ternary_end")

        result = self.builder.new_temp()

        # if (!condition) goto false_label
        self.builder.emit_if_false(condition, false_label)

        # True branch
        self.builder.emit_label(true_label)
        true_value = node.true_expr.accept(self)
        self.builder.emit_assign(result, true_value)
        self.builder.emit_goto(end_label)

        # False branch
        self.builder.emit_label(false_label)
        false_value = node.false_expr.accept(self)
        self.builder.emit_assign(result, false_value)

        # End
        self.builder.emit_label(end_label)

        return result

    def visit_new_expression(self, node: NewExpression) -> IRValue:
        """Visit new expression."""
        # Calculate size (simplified)
        size = IRConstant(8)  # Placeholder

        result = self.builder.new_temp()
        self.builder.emit_alloc(result, size)

        return result

    def visit_delete_expression(self, node: DeleteExpression) -> IRValue:
        """Visit delete expression."""
        ptr = node.expression.accept(self)
        self.builder.emit_free(ptr)

        return ptr

    def visit_this_expression(self, node: ThisExpression) -> IRValue:
        """Visit this expression."""
        return IRVariable("this")