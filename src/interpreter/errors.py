class MineScriptError(Exception):
    """Base class for all errors in the MineScript interpreter."""
    code = "UNKNOWN_ERROR"

class TypeMismatchError(MineScriptError):
    """Raised when a type mismatch occurs."""
    code = "E_TYPE_MISMATCH"
    
class UninitializedVariableError(MineScriptError):
    """Raised when an uninitialized variable is accessed."""
    code = "E_UNINITIALIZED"
    
class NonBoolConditionError(MineScriptError):
    """Raised when a non-boolean value is used in a conditional statement."""
    code = "E_NON_BOOL_CONDITION"
    
class BadOperandError(MineScriptError):
    """Raised when an invalid operand is used in an operation."""
    code = "E_BAD_OPERAND"
    
class BedrockHitError(MineScriptError):
    """Raised when a bedrock hit occurs."""
    code = "E_BEDROCK_HIT"
    
class NoGoldError(MineScriptError):
    """Raised when there is no gold available."""
    code = "E_NO_GOLD"
    
class BadArgError(MineScriptError):
    """Raised when a function is called with bad arguments."""
    code = "E_BAD_ARG"