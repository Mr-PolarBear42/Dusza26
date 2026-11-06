from errors import TypeMismatchError, UninitializedVariableError


class Environment:
    def __init__(self):
        # {name: {"value": value, "type": type}}
        self.variables = {}

    def get(self, name):
        if name not in self.variables:
            raise UninitializedVariableError(
                f"Variable '{name}' is not initialized."
            )
        return self.variables[name]["value"]

    def set(self, name, value):
        value_type = bool if isinstance(value, bool) else int
        if not isinstance(value, (bool, int)):
            raise TypeMismatchError("MineScript values must be integers or booleans.")
        if name in self.variables and self.variables[name]["type"] is not value_type:
            raise TypeMismatchError(f"Type mismatch for variable '{name}'.")
        self.variables[name] = {"value": value, "type": value_type}
