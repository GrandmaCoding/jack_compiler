from dataclasses import dataclass
from var_kind import VarKind


@dataclass
class VarInfo:
    """
    Stores information about a variable.
    
    Used by the code writer to track variable names,
    types, and scopes.
    
    Attributes:
        name: The variable name
        type_name: The variable type
        kind: The kind of variable (static, field, etc.)
        index: The index of the variable in its segment
    """
    name: str
    type_name: str
    kind: VarKind
    index: int 