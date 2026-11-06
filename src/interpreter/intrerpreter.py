from dataclasses import dataclass

from calc import Evaluator
from errors import *
from variable_env import Environment


KEYWORDS = {
    "and", "by", "else", "false", "forward", "here", "if", "isThere",
    "mine", "not", "or", "print", "set", "step", "to", "true", "turn", "while",
}


@dataclass
class DummyRobot:
    grid: list
    row: int
    column: int
    direction: str
    mined: int = 0

    DIRECTIONS = {"^": (-1, 0), ">": (0, 1), "v": (1, 0), "<": (0, -1)}

    @classmethod
    def from_map(cls, grid):
        for row, values in enumerate(grid):
            for column, value in enumerate(values):
                if value in cls.DIRECTIONS:
                    values[column] = "."
                    return cls(grid, row, column, value)
        raise ValueError("The map does not contain a robot.")

    def _ahead(self):
        dr, dc = self.DIRECTIONS[self.direction]
        return self.row + dr, self.column + dc

    def is_there(self, value):
        if type(value) is not int or value not in (0, 1, 2):
            raise BadArgError("isThere expects 0, 1, or 2.")
        row, column = self._ahead()
        if not (0 <= row < len(self.grid) and 0 <= column < len(self.grid[0])):
            found = 1
        else:
            cell = self.grid[row][column]
            found = 1 if cell == "#" else 2 if cell == "@" else 0
        return found == value

    def step(self, distance):
        if type(distance) is not int or distance < 0:
            raise BadArgError("step forward expects a non-negative integer.")
        for _ in range(distance):
            row, column = self._ahead()
            if (not 0 <= row < len(self.grid) or
                    not 0 <= column < len(self.grid[0]) or
                    self.grid[row][column] == "#"):
                raise BedrockHitError("The robot would hit bedrock.")
            self.row, self.column = row, column

    def turn(self, quarter_turns):
        if type(quarter_turns) is not int or quarter_turns < 0:
            raise BadArgError("turn by expects a non-negative integer.")
        directions = "^>v<"
        self.direction = directions[(directions.index(self.direction) - quarter_turns) % 4]

    def mine(self):
        if self.grid[self.row][self.column] != "@":
            raise NoGoldError("There is no gold here.")
        self.grid[self.row][self.column] = "."
        self.mined += 1


class Interpreter:
    def __init__(self, grid, source, instruction_limit=1000):
        self.robot = DummyRobot.from_map([list(row) for row in grid])
        self.lines = source.splitlines()
        self.environment = Environment()
        self.evaluator = Evaluator(self.environment, self.robot.is_there)
        self.instruction_limit = instruction_limit
        self.instruction_count = 0
        self.log = []
        self.output = []

    @staticmethod
    def _expression(tokens):
        if len(tokens) == 1:
            token = tokens[0]
            if token == "true":
                return ("literal", True)
            if token == "false":
                return ("literal", False)
            if token.isdigit():
                return ("literal", int(token))
            return ("name", token)
        if len(tokens) == 2 and tokens[0] == "isThere":
            return ("isThere", Interpreter._expression(tokens[1:]))
        if len(tokens) == 2 and tokens[0] == "not":
            return ("unary", "not", Interpreter._expression(tokens[1:]))
        if len(tokens) == 3:
            return ("binary", tokens[1], Interpreter._expression(tokens[:1]),
                    Interpreter._expression(tokens[2:]))
        raise ValueError("Invalid calculated value.")

    def _parse_command(self, tokens, line_number):
        head = tokens[0]
        if head == "step" and tokens[1] == "forward":
            return ("step", line_number, self._expression(tokens[2:]))
        if head == "turn" and tokens[1] == "by":
            return ("turn", line_number, self._expression(tokens[2:]))
        if head == "mine" and tokens[1] == "here":
            return ("mine", line_number)
        if head == "print":
            return ("print", line_number, self._expression(tokens[1:]))
        if head == "set" and tokens[2] == "to":
            return ("set", line_number, tokens[1], self._expression(tokens[3:]))
        if head in {"if", "while"}:
            return (head, line_number, self._expression(tokens[1:]))
        if head == "else":
            return ("else", line_number)
        raise ValueError(f"Unknown command: {head}")

    def _parse_block(self, index, indent):
        result = []
        while index < len(self.lines):
            raw = self.lines[index]
            current_indent = len(raw) - len(raw.lstrip(" "))
            if not raw.strip() or current_indent < indent:
                break
            if current_indent > indent:
                raise ValueError("Unexpected indentation.")
            tokens = raw.strip().split(" ")
            command = self._parse_command(tokens, index + 1)
            index += 1
            if command[0] in {"if", "while"}:
                if index >= len(self.lines):
                    body = []
                else:
                    child_indent = len(self.lines[index]) - len(self.lines[index].lstrip(" "))
                    body, index = self._parse_block(index, child_indent)
                command = command + (body,)
                if command[0] == "if" and index < len(self.lines):
                    next_indent = len(self.lines[index]) - len(self.lines[index].lstrip(" "))
                    if next_indent == indent and self.lines[index].strip().startswith("else"):
                        else_command = self._parse_command(
                            self.lines[index].strip().split(" "), index + 1)
                        index += 1
                        if index < len(self.lines):
                            child_indent = len(self.lines[index]) - len(self.lines[index].lstrip(" "))
                            else_body, index = self._parse_block(index, child_indent)
                        else:
                            else_body = []
                        command = command + (else_command[1], else_body)
            result.append(command)
        return result, index

    def parse(self):
        lines = [line for line in self.lines if line.strip()]
        self.lines = lines
        if not lines:
            return []
        indent = len(lines[0]) - len(lines[0].lstrip(" "))
        program, index = self._parse_block(0, indent)
        if index != len(lines):
            raise ValueError("Invalid block indentation.")
        return program

    @staticmethod
    def _format(value):
        return str(value).lower() if isinstance(value, bool) else str(value)

    def _begin(self, line_number):
        if self.instruction_count >= self.instruction_limit:
            self.log.append("INSTRUCTION_COUNT_LIMIT_EXCEEDED")
            raise StopIteration
        self.instruction_count += 1
        self.log.append(str(line_number))

    def _execute(self, command):
        kind, line = command[:2]
        self._begin(line)
        if kind == "set":
            self.environment.set(command[2], self.evaluator.evaluate(command[3]))
        elif kind == "step":
            value = self.evaluator.evaluate(command[2])
            self.robot.step(value)
            self.log[-1] += f" step forward {self._format(value)}"
        elif kind == "turn":
            value = self.evaluator.evaluate(command[2])
            self.robot.turn(value)
            self.log[-1] += f" turn by {self._format(value)}"
        elif kind == "mine":
            self.robot.mine()
            self.log[-1] += " mine here"
        elif kind == "print":
            value = self.evaluator.evaluate(command[2])
            self.output.append(value)
            self.log[-1] += f" print {self._format(value)}"
        elif kind == "if":
            condition = self.evaluator.evaluate(command[2])
            if type(condition) is not bool:
                raise NonBoolConditionError("if condition must be boolean.")
            branch = command[3] if condition else command[5]
            for child in branch:
                self._execute(child)
        elif kind == "while":
            while True:
                condition = self.evaluator.evaluate(command[2])
                if type(condition) is not bool:
                    raise NonBoolConditionError("while condition must be boolean.")
                if not condition:
                    break
                for child in command[3]:
                    self._execute(child)

    def run(self):
        try:
            for command in self.parse():
                self._execute(command)
        except StopIteration:
            return self.log
        except MineScriptError as error:
            self.log[-1] += f" {error.code}"
        self.log.append("EOR")
        return self.log


if __name__ == "__main__":
    # Example usage
    grid = [
        "#########",
        "#.......#",
        "#>......#",
        "#########"
    ]
    source = """
    set arany to isThere 2
    set count to 0
    turn by 0
    print arany
    if false
        print 1
    else
        set x to isThere 3
    print 9
    """
    interpreter = Interpreter(grid, source)
    log = interpreter.run()
    print("\n".join(log))