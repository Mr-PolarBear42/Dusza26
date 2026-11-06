class MineScriptError(Exception):
    code = "UNKNOWN_ERROR"


class TypeMismatchError(MineScriptError):
    code = "E_TYPE_MISMATCH"


class UninitializedVariableError(MineScriptError):
    code = "E_UNINITIALIZED"


class NonBoolConditionError(MineScriptError):
    code = "E_NON_BOOL_CONDITION"


class BadOperandError(MineScriptError):
    code = "E_BAD_OPERAND"


class BedrockHitError(MineScriptError):
    code = "E_BEDROCK_HIT"


class NoGoldError(MineScriptError):
    code = "E_NO_GOLD"


class BadArgError(MineScriptError):
    code = "E_BAD_ARG"
