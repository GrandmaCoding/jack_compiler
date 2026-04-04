from enum import Enum, auto


class VarKind(Enum):
    """Enum representing the kind of variable in the Jack language."""
    STATIC = auto()
    FIELD = auto()
    ARGUMENT = auto()
    LOCAL = auto()
    
    @classmethod
    def from_str(cls, kind_str: str) -> 'VarKind':
        """
        Convert a string to a VarKind.
        
        Args:
            kind_str: String representation of the kind
            
        Returns:
            Corresponding VarKind enum value
        """
        if kind_str == "static":
            return cls.STATIC
        elif kind_str == "field":
            return cls.FIELD
        elif kind_str == "arg":
            return cls.ARGUMENT
        elif kind_str == "var":
            return cls.LOCAL
        else:
            raise ValueError(f"Unknown var kind: {kind_str}") 