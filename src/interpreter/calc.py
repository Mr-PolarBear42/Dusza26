# Calc is short for calculator btw
from errors import BadOperandError, UninitializedVariableError

class Evaluator:
    def __init__(self, env, is_there=None, api_error=None):
        self.env = env
        self.is_there = is_there
        self.api_error = api_error

    def evaluate(self, expression):
        kind = expression[0] if isinstance(expression, tuple) else None
        if kind == "literal":
            return expression[1]
        if kind == "name":
            return self.env.get(expression[1])
        if kind == "isThere":
            if self.is_there is None:
                raise BadOperandError("isThere is unavailable without a robot.")
            try:
                argument = self.evaluate(expression[1])
            except UninitializedVariableError as error:
                if self.api_error is not None:
                    self.api_error("isThere", error)
                raise
            return self.is_there(argument)
        if kind == "unary":
            value = self.evaluate(expression[2])
            if expression[1] != "not" or not isinstance(value, bool):
                raise BadOperandError("Operand for 'not' must be boolean.")
            return not value
        if kind == "binary":
            left = self.evaluate(expression[2])
            right = self.evaluate(expression[3])
            operator = expression[1]
            if operator in {"+", "-", "*", "<", "<=", ">", ">="}:
                if type(left) is not int or type(right) is not int:
                    raise BadOperandError("This operator requires integer operands.")
                return {
                    "+": lambda: left + right, 
                    "-": lambda: left - right,
                    "*": lambda: left * right, 
                    "<": lambda: left < right,
                    "<=": lambda: left <= right, 
                    ">": lambda: left > right,
                    ">=": lambda: left >= right,
                }[operator]()
            if operator in {"=", "<>"}:
                if type(left) is not type(right):
                    raise BadOperandError("Equality operands must have matching types.")
                return left == right if operator == "=" else left != right
            if operator in {"and", "or"}:
                if type(left) is not bool or type(right) is not bool:
                    raise BadOperandError("Logical operands must be booleans.")
                return left and right if operator == "and" else left or right
        raise BadOperandError("Invalid expression.")
