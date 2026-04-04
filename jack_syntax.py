from dataclasses import dataclass, field
from typing import List, Optional, Any, Tuple, Union

from .jack_token import JackToken


@dataclass
class ClassSyntax:
    """Represents a Jack class."""
    class_keyword: JackToken
    name: JackToken
    open_brace: JackToken
    var_decs: List["ClassVarDecSyntax"]
    subroutines: List["SubroutineDecSyntax"]
    close_brace: JackToken


@dataclass
class ClassVarDecSyntax:
    """Represents a class variable declaration (field or static)."""
    kind_keyword: JackToken  # 'field' or 'static'
    type_token: JackToken    # 'int', 'char', 'boolean', or a class name
    names: List[JackToken]   # Variable names
    semicolon: JackToken


@dataclass
class Parameter:
    """Represents a parameter in a subroutine declaration."""
    type_token: JackToken
    name: JackToken


@dataclass
class ParameterListSyntax:
    """Represents a parameter list in a subroutine declaration."""
    parameters: List[Parameter]


@dataclass
class SubroutineDecSyntax:
    """Represents a subroutine declaration (method, function, or constructor)."""
    keyword: JackToken       # 'method', 'function', or 'constructor'
    return_type: JackToken   # 'void', 'int', 'char', 'boolean', or a class name
    name: JackToken
    open_paren: JackToken
    parameters: ParameterListSyntax
    close_paren: JackToken
    body: "SubroutineBodySyntax"


@dataclass
class SubroutineBodySyntax:
    """Represents the body of a subroutine."""
    open_brace: JackToken
    var_decs: List["VarDecSyntax"]
    statements: "StatementsSyntax"
    close_brace: JackToken


@dataclass
class VarDecSyntax:
    """Represents a variable declaration."""
    var_keyword: JackToken
    type_token: JackToken
    names: List[JackToken]
    semicolon: JackToken


@dataclass
class StatementsSyntax:
    """Represents a list of statements."""
    statements: List["StatementSyntax"]


@dataclass
class StatementSyntax:
    """Base class for statements."""
    pass


@dataclass
class LetStatementSyntax(StatementSyntax):
    """Represents a let statement."""
    let_keyword: JackToken
    var_name: JackToken
    indexing: Optional["Indexing"]
    equals: JackToken
    value: "ExpressionSyntax"
    semicolon: JackToken


@dataclass
class Indexing:
    """Represents array indexing."""
    open_bracket: JackToken
    index: "ExpressionSyntax"
    close_bracket: JackToken


@dataclass
class IfStatementSyntax(StatementSyntax):
    """Represents an if statement."""
    if_keyword: JackToken
    open_paren: JackToken
    condition: "ExpressionSyntax"
    close_paren: JackToken
    open_true: JackToken
    true_statements: StatementsSyntax
    close_true: JackToken
    else_clause: Optional["ElseClause"]


@dataclass
class ElseClause:
    """Represents an else clause in an if statement."""
    else_keyword: JackToken
    open_brace: JackToken
    statements: StatementsSyntax
    close_brace: JackToken


@dataclass
class WhileStatementSyntax(StatementSyntax):
    """Represents a while statement."""
    while_keyword: JackToken
    open_paren: JackToken
    condition: "ExpressionSyntax"
    close_paren: JackToken
    open_brace: JackToken
    statements: StatementsSyntax
    close_brace: JackToken


@dataclass
class DoStatementSyntax(StatementSyntax):
    """Represents a do statement."""
    do_keyword: JackToken
    subroutine_call: "SubroutineCall"
    semicolon: JackToken


@dataclass
class ReturnStatementSyntax(StatementSyntax):
    """Represents a return statement."""
    return_keyword: JackToken
    expression: Optional["ExpressionSyntax"]
    semicolon: JackToken


@dataclass
class ExpressionSyntax:
    """Represents an expression."""
    first_term: "TermSyntax"
    operations: List[Tuple[JackToken, "TermSyntax"]] = field(default_factory=list)


@dataclass
class TermSyntax:
    """Base class for terms."""
    pass


@dataclass
class IntegerConstantTerm(TermSyntax):
    """Represents an integer constant."""
    token: JackToken


@dataclass
class StringConstantTerm(TermSyntax):
    """Represents a string constant."""
    token: JackToken


@dataclass
class KeywordConstantTerm(TermSyntax):
    """Represents a keyword constant (true, false, null, this)."""
    token: JackToken


@dataclass
class VarNameTerm(TermSyntax):
    """Represents a variable name."""
    name: JackToken


@dataclass
class IndexedVarTerm(TermSyntax):
    """Represents an indexed variable (array access)."""
    name: JackToken
    indexing: Indexing


@dataclass
class ParenthesizedTerm(TermSyntax):
    """Represents a parenthesized expression."""
    open_paren: JackToken
    expression: ExpressionSyntax
    close_paren: JackToken


@dataclass
class UnaryOpTerm(TermSyntax):
    """Represents a unary operation."""
    operator: JackToken
    term: TermSyntax


@dataclass
class SubroutineCallTerm(TermSyntax):
    """Represents a subroutine call as a term."""
    call: "SubroutineCall"


@dataclass
class SubroutineCall:
    """Represents a subroutine call."""
    obj_name: Optional[JackToken]
    dot: Optional[JackToken]
    subroutine_name: JackToken
    open_paren: JackToken
    arguments: "ExpressionListSyntax"
    close_paren: JackToken


@dataclass
class ExpressionListSyntax:
    """Represents a list of expressions."""
    expressions: List[ExpressionSyntax] = field(default_factory=list) 