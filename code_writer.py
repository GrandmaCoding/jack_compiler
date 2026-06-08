from typing import Dict, List, Optional

from var_info import VarInfo
from var_kind import VarKind
from jack_syntax import (
    ClassSyntax, ClassVarDecSyntax, SubroutineDecSyntax, SubroutineBodySyntax,
    StatementsSyntax, LetStatementSyntax, IfStatementSyntax, WhileStatementSyntax,
    DoStatementSyntax, ReturnStatementSyntax, ExpressionSyntax, TermSyntax,
    IntegerConstantTerm, StringConstantTerm, KeywordConstantTerm, VarNameTerm,
    IndexedVarTerm, ParenthesizedTerm, UnaryOpTerm, SubroutineCallTerm,
    SubroutineCall, ExpressionListSyntax
)


class CodeWriter:
    """
    Generates VM code from Jack AST.

    This is the core of the compiler, which translates
    the parsed Jack syntax into VM instructions.
    """

    def __init__(self, class_symbols: Optional[Dict[str, VarInfo]] = None,
                method_symbols: Optional[Dict[str, VarInfo]] = None):
        self.result_vm_code: List[str] = []
        self.class_symbols = class_symbols or {}
        self.method_symbols = method_symbols or {}
        self.current_class_name = "Main"
        self.label_counter = 0

    def write(self, line: str) -> None:
        """Add a line of VM code to the result."""
        self.result_vm_code.append(line)

    def find_var_info(self, var_name: str) -> Optional[VarInfo]:
        """
        Find variable information by name.
        Checks local (method) variables first, then class variables.
        """
        if var_name in self.method_symbols:
            return self.method_symbols[var_name]
        elif var_name in self.class_symbols:
            return self.class_symbols[var_name]
        else:
            return None

    def _push_var(self, var_info: VarInfo) -> None:
        """Generate VM code to push a variable's value onto the stack."""
        segment = self._get_segment(var_info.kind)
        self.write(f"push {segment} {var_info.index}")

    def _pop_var(self, var_info: VarInfo) -> None:
        """Generate VM code to pop a value from the stack into a variable."""
        segment = self._get_segment(var_info.kind)
        self.write(f"pop {segment} {var_info.index}")

    def _get_segment(self, kind: VarKind) -> str:
        """Convert a variable kind to a VM segment name."""
        if kind == VarKind.STATIC:
            return "static"
        elif kind == VarKind.FIELD:
            return "this"
        elif kind == VarKind.ARGUMENT:
            return "argument"
        elif kind == VarKind.LOCAL:
            return "local"
        else:
            raise ValueError(f"Unknown var kind: {kind}")

    def _get_next_label(self, label_prefix: str) -> str:
        """Generate a unique label."""
        label = f"{label_prefix}_{self.label_counter}"
        self.label_counter += 1
        return label

    def write_class(self, class_syntax: ClassSyntax) -> None:
        """
        Generate VM code for a class.

        Args:
            class_syntax: The class syntax to generate code for
        """
        self.current_class_name = class_syntax.name.value
        self.class_symbols = {}
        
        static_index = 0
        field_index = 0
        
        for var_declaration in class_syntax.var_decs:
            kind_value = var_declaration.kind_keyword.value
            var_kind = VarKind.from_str(kind_value)
            type_name = var_declaration.type_token.value
            
            for name_token in var_declaration.names:
                name = name_token.value
                if var_kind == VarKind.STATIC:
                    self.class_symbols[name] = VarInfo(name, type_name, var_kind, static_index)
                    static_index += 1
                elif var_kind == VarKind.FIELD:
                    self.class_symbols[name] = VarInfo(name, type_name, var_kind, field_index)
                    field_index += 1
        
        for subroutine in class_syntax.subroutines:
            self.write_subroutine(subroutine)

    def write_subroutine(self, subroutine: SubroutineDecSyntax) -> None:
        """
        Generate VM code for a subroutine.

        Args:
            subroutine: The subroutine syntax to generate code for
        """
        self.method_symbols = {}
        
        kind_of_string = subroutine.keyword.value
        subroutine_name = subroutine.name.value

        argument_index = 0
        if kind_of_string == 'method':
            argument_index = 1
        
        for parameter in subroutine.parameters.parameters:
            name = parameter.name.value
            type_name = parameter.type_token.value
            self.method_symbols[name] = VarInfo(name, type_name, VarKind.ARGUMENT, argument_index)
            argument_index += 1
        
        local_index = 0
        for var_declaration in subroutine.body.var_decs:
            type_name = var_declaration.type_token.value
            for name_token in var_declaration.names:
                name = name_token.value
                self.method_symbols[name] = VarInfo(name, type_name, VarKind.LOCAL, local_index)
                local_index += 1
        
        function_name = f"{self.current_class_name}.{subroutine_name}"
        self.write(f"function {function_name} {local_index}")
        
        if kind_of_string == 'constructor':
            amount_of_fields = 0
            for var_info in self.class_symbols.values():
                if var_info.kind == VarKind.FIELD:
                    amount_of_fields += 1
            
            if amount_of_fields > 0:
                self.write(f"push constant {amount_of_fields}")
                self.write("call Memory.alloc 1")
                self.write("pop pointer 0")
        elif kind_of_string == 'method':
            self.write("push argument 0")
            self.write("pop pointer 0")
            
        self.write_statements(subroutine.body.statements)

    def write_expression(self, expression: ExpressionSyntax) -> None:
        """
        Generate VM code for an expression.

        An expression is: first_term (op term)*
        Operators: + - * / & | < > =
        """
        op_map = {
            '+': 'add',
            '-': 'sub',
            '*': 'call Math.multiply 2',
            '/': 'call Math.divide 2',
            '&': 'and',
            '|': 'or',
            '<': 'lt',
            '>': 'gt',
            '=': 'eq'
        }

        self.write_term(expression.first_term)
        for op_token, term in expression.operations:
            self.write_term(term)
            vm_command = op_map.get(op_token.value)
            if vm_command:
                self.write(vm_command)

    def write_term(self, term: TermSyntax) -> None:
        """
        Generate VM code for a term.

        Term types to handle:
        - IntegerConstantTerm: push constant N
        - StringConstantTerm: String.new(len) + appendChar for each char
        - KeywordConstantTerm: true=-1, false/null=0, this=pointer 0
        - VarNameTerm: push variable (use find_var_info + _push_var)
        - IndexedVarTerm: array access - base+index, pop pointer 1, push that 0
        - ParenthesizedTerm: evaluate inner expression
        - UnaryOpTerm: evaluate term, then neg (-) or not (~)
        - SubroutineCallTerm: delegate to write_subroutine_call
        """
        match term:
            case IntegerConstantTerm(token=token):
                self.write(f'push constant {token.int_value}')

            case StringConstantTerm(token=token):
                string_val = token.value
                self.write(f'push constant {len(string_val)}')
                self.write('call String.new 1')
                for char in string_val:
                    self.write(f'push constant {ord(char)}')
                    self.write('call String.appendChar 2')

            case KeywordConstantTerm(token=token):
                match token.value:
                    case 'true':
                        self.write('push constant 1')
                        self.write('neg')
                    case 'false' | 'null':
                        self.write('push constant 0')
                    case 'this':
                        self.write('push pointer 0')

            case VarNameTerm(name=name):
                var_info = self.find_var_info(name.value)
                self._push_var(var_info)

            case IndexedVarTerm(name=name, indexing=indexing):
                var_info = self.find_var_info(name.value)
                self._push_var(var_info)
                self.write_expression(indexing.index)
                self.write('add')
                self.write('pop pointer 1')
                self.write('push that 0')

            case ParenthesizedTerm(expression=expression):
                self.write_expression(expression)

            case UnaryOpTerm(term=inner_term, operator=operator):
                self.write_term(inner_term)
                match operator.value:
                    case '-': self.write('neg')
                    case '~': self.write('not')

            case SubroutineCallTerm(call=call):
                self.write_subroutine_call(call)

    def write_subroutine_call(self, call: SubroutineCall) -> None:
        """
        Generate VM code for a subroutine call.

        Three cases:
        - f(args): method on current object
        - obj.f(args): method on object
        - Class.f(args): static/function call
        """
        args = call.arguments
        num_args = len(args.expressions)
        sub_name = call.subroutine_name.value

        # Случай 1: f(args) -> метод текущего класса
        if call.obj_name is None:
            self.write('push pointer 0')
            func_name = f'{self.current_class_name}.{sub_name}'
            num_args += 1
            
        # Случаи 2 и 3: есть объект или класс перед точкой
        else:
            obj_name = call.obj_name.value
            var_info = self.find_var_info(obj_name)
            
            if var_info is not None:
                # Случай 2: obj.f(args) -> метод объекта
                self._push_var(var_info)
                func_name = f'{var_info.type_name}.{sub_name}'
                num_args += 1
            else:
                # Случай 3: Class.f(args) -> статический метод/функция
                func_name = f'{obj_name}.{sub_name}'

        # Единая точка вызова
        self._write_subroutine_call_with_args(func_name, args, num_args)

    def _write_subroutine_call_with_args(self, func_name: str,
                                         args: ExpressionListSyntax,
                                         num_args: int) -> None:
        """Push all arguments then emit call func_name num_args."""
        for expression in args.expressions:
            self.write_expression(expression)
        self.write(f'call {func_name} {num_args}')

    def write_statements(self, statements: StatementsSyntax) -> None:
        """
        Generate VM code for a list of statements.
        Dispatch each statement to the appropriate write_*_statement method.
        """
        for stmt in statements.statements:
            match stmt:
                case LetStatementSyntax():    self.write_let_statement(stmt)
                case IfStatementSyntax():     self.write_if_statement(stmt)
                case WhileStatementSyntax():  self.write_while_statement(stmt)
                case DoStatementSyntax():     self.write_do_statement(stmt)
                case ReturnStatementSyntax(): self.write_return_statement(stmt)

    def write_let_statement(self, statement: LetStatementSyntax) -> None:
        """
        Generate VM code for a let statement.

        Simple: let x = expr -> evaluate expr, pop to variable
        Array:  let a[i] = expr -> compute base+index, evaluate expr, store via THAT
        """
        var_name = statement.var_name.value
        var_info = self.find_var_info(var_name)
        
        if var_info is None:
            raise ValueError(f"Variable '{var_name}' is not defined.")

        # Случай 1: Обычное присваивание (let x = expr)
        if statement.indexing is None:
            self.write_expression(statement.value)
            self._pop_var(var_info)
            return

        # Случай 2: Присваивание в массив (let a[i] = expr)
        # Вычисляем целевой адрес: base + index
        self._push_var(var_info)
        self.write_expression(statement.indexing.index)
        self.write('add')
        
        # Вычисляем выражение справа
        self.write_expression(statement.value)
        
        # Переносим значение выражения в массив
        self.write('pop temp 0')     # Сохраняем значение выражения
        self.write('pop pointer 1')  # Восстанавливаем базовый адрес массива в THAT
        self.write('push temp 0')    # Возвращаем значение выражения на стек
        self.write('pop that 0')     # Записываем в ячейку памяти

    def write_if_statement(self, statement: IfStatementSyntax) -> None:
        """
        Generate VM code for an if statement.

        Pattern: evaluate condition, not, if-goto ELSE, [true branch], goto END, label ELSE, [else branch], label END
        """
        # Сначала вычисляем условие
        self.write_expression(statement.condition)
        self.write('not')

        # Случай 1: Классический IF-ELSE
        if statement.else_clause is not None:
            else_label = self._get_next_label('IF_ELSE')
            end_label = self._get_next_label('IF_END')

            self.write(f'if-goto {else_label}')
            self.write_statements(statement.true_statements)
            self.write(f'goto {end_label}')
            
            self.write(f'label {else_label}')
            self.write_statements(statement.else_clause.statements)
            self.write(f'label {end_label}')
            
        # Случай 2: Простой IF без else
        else:
            end_label = self._get_next_label('IF_END')
            
            self.write(f'if-goto {end_label}')
            self.write_statements(statement.true_statements)
            self.write(f'label {end_label}')

    def write_while_statement(self, statement: WhileStatementSyntax) -> None:
        """
        Generate VM code for a while statement.

        Pattern: label WHILE, evaluate condition, not, if-goto END, [body], goto WHILE, label END
        """
        exp_label = self._get_next_label('WHILE_EXP')
        end_label = self._get_next_label('WHILE_END')
        
        self.write(f'label {exp_label}')
        self.write_expression(statement.condition)
        self.write('not')
        self.write(f'if-goto {end_label}')
        
        self.write_statements(statement.statements)
        self.write(f'goto {exp_label}')
        self.write(f'label {end_label}')

    def write_do_statement(self, statement: DoStatementSyntax) -> None:
        """
        Generate VM code for a do statement.
        Call the subroutine, then discard the return value (pop temp 0).
        """
        self.write_subroutine_call(statement.subroutine_call)
        self.write('pop temp 0')

    def write_return_statement(self, statement: ReturnStatementSyntax) -> None:
        """
        Generate VM code for a return statement.
        If expression present: evaluate it. Otherwise push constant 0 (void).
        Then emit 'return'.
        """
        match statement.expression:
            case None:
                self.write('push constant 0')
            case expression:
                self.write_expression(expression)
                
        self.write('return')
