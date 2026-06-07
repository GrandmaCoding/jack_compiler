from typing import Dict, List, Optional, Any, Set, Tuple

from .var_info import VarInfo
from .var_kind import VarKind
from .jack_syntax import (
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
        """
        Initialize the code writer.

        Args:
            class_symbols: Dictionary of class-level variables
            method_symbols: Dictionary of method-level variables
        """
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

        Checks local variables first, then class variables.

        Args:
            var_name: The name of the variable to find

        Returns:
            The variable information or None if not found
        """
        if var_name in self.method_symbols:
            return self.method_symbols[var_name]
        elif var_name in self.class_symbols:
            return self.class_symbols[var_name]
        else:
            return None

    def _get_segment(self, kind: VarKind) -> str:
        """
        Convert a variable kind to a VM segment name.

        Args:
            kind: The variable kind

        Returns:
            The corresponding VM segment name
        """
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

    def _push_var(self, var_info: VarInfo) -> None:
        """
        Generate VM code to push a variable's value onto the stack.

        Args:
            var_info: Information about the variable
        """
        segment = self._get_segment(var_info.kind)
        self.write(f"push {segment} {var_info.index}")

    def _pop_var(self, var_info: VarInfo) -> None:
        """
        Generate VM code to pop a value from the stack into a variable.

        Args:
            var_info: Information about the variable
        """
        segment = self._get_segment(var_info.kind)
        self.write(f"pop {segment} {var_info.index}")

    def _get_next_label(self, label_prefix: str) -> str:
        """
        Generate a unique label.

        Args:
            label_prefix: A prefix for the label

        Returns:
            A unique label
        """
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
        
        for var_dec in class_syntax.var_decs:
            kind_of_string = var_dec.kind_keyword.value
            kind = VarKind.from_str(kind_of_string)
            type_name = var_dec.type_token.value
            
            for name_token in var_dec.names:
                name = name_token.value
                if kind == VarKind.STATIC:
                    self.class_symbols[name] = VarInfo(name, type_name, kind, static_index)
                    static_index += 1
                elif kind == VarKind.FIELD:
                    self.class_symbols[name] = VarInfo(name, type_name, kind, field_index)
                    field_index += 1
        
        for subroutine in class_syntax.subroutines:
            self.write_subroutine(subroutine)

    def write_subroutine(self, subroutine: SubroutineDecSyntax) -> None:
        """
        Generate VM code for a subroutine.

        Args:
            subroutine: The subroutine syntax to generate code for
        """
        raise NotImplementedError()

    def write_statements(self, statements: StatementsSyntax) -> None:
        """
        Generate VM code for statements.

        Args:
            statements: The statements to generate code for
        """
        pass

    def write_let_statement(self, statement: LetStatementSyntax) -> None:
        """
        Generate VM code for a let statement.

        Args:
            statement: The let statement to generate code for
        """
        pass

    def write_if_statement(self, statement: IfStatementSyntax) -> None:
        """
        Generate VM code for an if statement.

        Args:
            statement: The if statement to generate code for
        """
        pass

    def write_while_statement(self, statement: WhileStatementSyntax) -> None:
        """
        Generate VM code for a while statement.

        Args:
            statement: The while statement to generate code for
        """
        pass

    def write_do_statement(self, statement: DoStatementSyntax) -> None:
        """
        Generate VM code for a do statement.

        Args:
            statement: The do statement to generate code for
        """
        pass

    def write_return_statement(self, statement: ReturnStatementSyntax) -> None:
        """
        Generate VM code for a return statement.

        Args:
            statement: The return statement to generate code for
        """
        pass

    def write_expression(self, expression: ExpressionSyntax) -> None:
        """
        Generate VM code for an expression.

        Args:
            expression: The expression to generate code for
        """
        pass

    def write_term(self, term: TermSyntax) -> None:
        """
        Generate VM code for a term.

        Args:
            term: The term to generate code for
        """
        pass

    def write_subroutine_call(self, call: SubroutineCall) -> None:
        """
        Generate VM code for a subroutine call.

        Args:
            call: The subroutine call to generate code for
        """
        pass
