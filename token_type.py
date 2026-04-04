from enum import Flag, auto


class TokenType(Flag):
    """Enum representing the different types of tokens in the Jack language."""
    SYMBOL = auto()
    KEYWORD = auto()
    INTEGER_CONSTANT = auto()
    STRING_CONSTANT = auto()
    IDENTIFIER = auto() 