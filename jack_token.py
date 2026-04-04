from dataclasses import dataclass
from .token_type import TokenType


@dataclass
class JackToken:
    """
    Represents a token in the Jack language.
    
    Attributes:
        token_type: The type of token (keyword, symbol, etc.)
        value: The string value of the token
        line_number: The line number where the token appears
        col_number: The column number where the token appears
    """
    token_type: TokenType
    value: str
    line_number: int
    col_number: int
    
    @property
    def int_value(self) -> int:
        """Convert the token value to an integer."""
        return int(self.value)
    
    def __str__(self) -> str:
        """String representation of the token."""
        return f"[{self.token_type.name} {self.value}] at line {self.line_number}, col {self.col_number}" 