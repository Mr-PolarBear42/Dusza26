from errors import *
class Environment:
    def __init__(self):
        # Stores variables as a dictionary with their values and types
        # Example: {"var_name": {"value": 10, "type": "int"}}
        self.variables = {}

    def get(self, name):
        if name not in self.variables:
            raise UninitializedVariableError(f"Variable '{name}' is not initialized.")
        return self.variables[name]
    
    def set(self, name, value):
        val_type = (int if isinstance(value, int) and not isinstance(value, bool) else "bool")
        if name in self.variables:
            #check if type matches existing variable type
            if self.variables[name]["type"] != val_type:
                raise TypeMismatchError(f"Type mismatch for variable '{name}'. Expected {self.variables[name]['type']}, got {val_type}.")
            self.variables[name] = {"value": value, "type": val_type}
        else:
            # If the variable is not initialized, we can initialize it with the new value and type
            self.variables[name] = {"value": value, "type": val_type}
            
        
        