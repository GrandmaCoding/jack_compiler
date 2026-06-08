from typing import Optional
from jack_token import JackToken

class ExpectedException(Exception):
    """Exception raised when an unexpected token is encountered."""
    
    def __init__(self, expected: str, actual: Optional[JackToken]):
        self.expected = expected
        self.actual = actual
        actual_repr = repr(actual) if actual else "None"
        line = getattr(actual, 'line_number', 'N/A') 
        col = getattr(actual, 'col_number', 'N/A')
        message = f"Expected {expected}, got {actual_repr} at Line: {line}, Col: {col}"
        super().__init__(message) 