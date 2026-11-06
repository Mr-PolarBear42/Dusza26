from errors import *
from variable_env import Environment
from calc import Evaluator
# from robot import Robot #TODO: Implement robot class and import it here

class InterpreterEngine:
    def __init__(self, robot_instance):
        self.env = Environment()
        self.evaluator = Evaluator(self.env)
        self.robot = robot_instance #TODO: Implement robot instance usage in the interpreter
        self.instruction_count=0
        self.max_instructions=1000 #TODO: Make this configurable
        
    def check_instruction_limit(self):
        """Checks if the instruction count has exceeded the maximum allowed."""
        if self.instruction_count >= self.max_instructions:
            raise MineScriptError("Instruction limit exceeded.")
        
    def execute_set(self, var_name, value):
        """Executes a variable assignment."""
        self.check_instruction_limit()
        evaluated_value = self.evaluator.evaluate(value)
        self.env.set(var_name, evaluated_value)
        self.instruction_count += 1
    
    def execute
    