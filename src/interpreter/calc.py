############################################################################################
# If anyone joind the stream recently "calc" stands for "calculator", I'm just using slang #
############################################################################################

from errors import *

class Evaluator:

  def __init__(self, env):
    self.env = env

  def evaluate(self, token):
    """Evaluates a simple value or literal."""
    if isinstance(token, int) or isinstance(token, bool):
      return token
    if isinstance(token, str):
      if token.lower() == "true":
        return True
      if token.lower() == "false":
        return False
      if token.isdigit():
        return int(token)
      # Otherwise, it's a variable identifier
      return self.env.get(token)
    return token

  def evaluate_binary(self, left, op, right):
    l_val = self.evaluate(left)
    r_val = self.evaluate(right)

    # Arithmetic operators (+, -, *)
    if op in ("+", "-", "*"):
      if not isinstance(l_val, int) or not isinstance(r_val, int):
        raise BadOperandError("Arithmetic operands must be integers.")
      if op == "+":
        return l_val + r_val
      if op == "-":
        return l_val - r_val
      if op == "*":
        return l_val * r_val

    # Comparison operators (<, <=, >, >=)
    elif op in ("<", "<=", ">", ">="):
      if not isinstance(l_val, int) or not isinstance(r_val, int):
        raise BadOperandError("Comparison operands must be integers.")
      if op == "<":
        return l_val < r_val
      if op == "<=":
        return l_val <= r_val
      if op == ">":
        return l_val > r_val
      if op == ">=":
        return l_val >= r_val

    # Equality operators (=, <>)
    elif op in ("=", "<>"):
      if type(l_val) != type(r_val):
        raise BadOperandError("Equality operands must have matching types.")
      if op == "=":
        return l_val == r_val
      if op == "<>":
        return l_val != r_val

    # Logical operators (and, or)
    elif op in ("and", "or"):
      if not isinstance(l_val, bool) or not isinstance(r_val, bool):
        raise BadOperandError("Logical operands must be booleans.")
      if op == "and":
        return l_val and r_val
      if op == "or":
        return l_val or r_val

    raise BadOperandError(f"Unknown operator {op}")

  def evaluate_unary(self, op, val_token):
    val = self.evaluate(val_token)
    if op == "not":
      if not isinstance(val, bool):
        raise BadOperandError("Operand for 'not' must be boolean.")
      return not val
    raise BadOperandError(f"Unknown unary operator {op}")