from dataclasses import dataclass
from typing import Any

from .errors import InstructionLimitExceeded, ProgramTerminated, RuntimeErrorCode
from .logging import ExecutionLog
from .robot import Robot
from .state_snapshot import StateSnapshot

KEYWORDS = {
    "and",
    "by",
    "else",
    "false",
    "forward",
    "here",
    "if",
    "isThere",
    "mine",
    "not",
    "or",
    "print",
    "set",
    "step",
    "to",
    "true",
    "turn",
    "while",
}


@dataclass
class _Command:
    line: int
    tokens: list[str]
    body: list[_Command] | None = None
    otherwise: list[_Command] | None = None
    else_line: int | None = None


class Interpreter:
    def __init__(self, robot: Robot, max_instructions: int = 1000) -> None:
        self.robot = robot
        self.max_instructions = max_instructions
        self.variables: dict[str, Any] = {}
        self.log = ExecutionLog()
        self._instruction_count = 0
        self._current_line = 0
        self._api_error: tuple[str, Any] | None = None
        self.state_snapshots: list[StateSnapshot] = []
        self.entry_snapshots: list[StateSnapshot] = []
        self.entry_log_indices: list[int] = []

    def reset(self) -> None:
        """Resets the Interpreter to its initial state, clearing variables and logs."""
        self.variables = {}
        self.log = ExecutionLog()
        self.state_snapshots = []
        self.entry_snapshots = []
        self.entry_log_indices = []
        self._instruction_count = 0
        self._current_line = 0
        self._api_error = None

    def run(self, source: str) -> ExecutionLog:
        """Runs the code provided in the source string, executing commands and logging the results.

        Args:
            source (str): The source code to be executed by the interpreter.

        Returns:
            ExecutionLog: An ExecutionLog object containing the results of the execution, including any errors encountered.
        Raises:
            InstructionLimitExceeded: If the number of executed instructions exceeds the maximum allowed.
            ProgramTerminated: If the program is terminated due to an error.
        """
        self.reset()
        commands = _parse(source)
        try:
            self._execute_block(commands)
        except InstructionLimitExceeded:
            self.log.add_limit_error()
            return self.log
        except ProgramTerminated:
            pass
        self.log.finish()
        return self.log

    def _execute_block(self, commands: list[_Command]) -> None:
        """Executes a block of commands, handling each command in sequence.

        Args:
            commands (list[_Command]): The commands to be executed in the block.
        """
        for command in commands:
            self._execute(command)

    def _execute(self, command: _Command) -> None:
        """Executes a Single command, handling instruction counting and error logging.

        Args:
            command (_Command): The command to be executed.

        Raises:
            InstructionLimitExceeded: If the number of executed instructions exceeds the maximum allowed.
            ProgramTerminated: If the program is terminated due to an error during command execution.
        """
        self._instruction_count += 1
        if self._instruction_count > self.max_instructions:
            raise InstructionLimitExceeded
        self._current_line = command.line
        self._api_error = None
        self.entry_snapshots.append(
            StateSnapshot(
                self.variables.copy(),
                command.line,
                (self.robot.row, self.robot.column),
                self.robot.direction,
                self.robot.mined_positions,
                self.robot.discovered
            )
        )
        self.entry_log_indices.append(len(self.log.lines))
        try:
            self._execute_inner(command)
        except RuntimeErrorCode as error:
            if self._api_error is None:
                self.log.record(command.line, error=error.code)
            else:
                api, value = (
                    self._api_error
                )  # ??? Nem tudom miért, de a type checker szerint ez így nem ok, de hibát nem ad
                details = () if value is None else (value,)
                self.log.record(command.line, api, *details, error=error.code)
            raise ProgramTerminated from error
        self.state_snapshots.append(
            StateSnapshot(
                self.variables.copy(),
                command.line,
                (self.robot.row, self.robot.column),
                self.robot.direction,
                self.robot.mined_positions,
                self.robot.discovered
            )
        )

    def _execute_inner(self, command: _Command) -> None:
        """Executes the inner logic of a command, determining the type of command and performing the appropriate action.

        Args:
            command (_Command): The command to be executed.

        Raises:
            RuntimeErrorCode: If an error occurs during command execution, such as a bad argument or type mismatch.
        """
        tokens = command.tokens
        keyword = tokens[0]
        if keyword == "set":
            self._set(command)
        elif keyword == "if":
            self._condition(command)
        elif keyword == "while":
            first_iteration = True
            while True:
                if not first_iteration:
                    self._consume_instruction()
                first_iteration = False
                condition = self._evaluate(tokens[1])
                if not isinstance(condition, bool):
                    raise RuntimeErrorCode("E_NON_BOOL_CONDITION")
                self._log_control(command)
                if not condition:
                    break
                self._execute_block(command.body or [])
        elif keyword == "step":
            self._api_error = ("step forward", None)
            value = self._evaluate(tokens[2])
            if not isinstance(value, int) or isinstance(value, bool):
                self._api_error = ("step forward", value)
                raise RuntimeErrorCode("E_BAD_ARG")
            self._api(
                command, "step forward", value, lambda: self.robot.step_forward(value)
            )
        elif keyword == "turn":
            self._api_error = ("turn by", None)
            value = self._evaluate(tokens[2])
            if not isinstance(value, int) or isinstance(value, bool):
                self._api_error = ("turn by", value)
                raise RuntimeErrorCode("E_BAD_ARG")
            self._api(command, "turn by", value, lambda: self.robot.turn_by(value))
        elif keyword == "mine":
            self._api(command, "mine here", None, self.robot.mine_here)
        elif keyword == "print":
            value = self._evaluate(tokens[1])
            self._api(command, "print", value, lambda: None)
        else:
            raise RuntimeErrorCode("E_BAD_ARG")

    def _set(self, command: _Command) -> None:
        """Sets a variable to a calculated value, checking for type mismatches and logging the operation.

        Args:
            command (_Command): Command containing the variable name and the expression to be evaluated.

        Raises:
            RuntimeErrorCode: E_TYPE_MISMATCH if the variable already exists and the new value's type does not match the existing type.
        """
        log_length = len(self.log.lines)
        value = self._evaluate_calculated(command.tokens[3:])
        if command.tokens[1] in self.variables and type(
            self.variables[command.tokens[1]]
        ) is not type(value):
            raise RuntimeErrorCode("E_TYPE_MISMATCH")
        self.variables[command.tokens[1]] = value
        if len(self.log.lines) == log_length:
            self.log.record(command.line)

    def _condition(self, command: _Command) -> None:
        """Evaluates a condition for an 'if' command and executes the appropriate block of commands based on the result."""
        condition = self._evaluate(command.tokens[1])
        if not isinstance(condition, bool):
            raise RuntimeErrorCode("E_NON_BOOL_CONDITION")
        self._log_control(command)
        if condition:
            self._execute_block(command.body or [])
        elif command.otherwise is not None:
            if command.else_line is not None:
                self._instruction_count += 1
                if self._instruction_count > self.max_instructions:
                    raise InstructionLimitExceeded
                self.log.record(command.else_line)
            self._execute_block(command.otherwise)

    def _log_control(self, command: _Command) -> None:
        """Logs the control flow of a command"""
        self.log.record(command.line)

    def _consume_instruction(self) -> None:
        """
        Increments the instruction count and checks if it exceeds the maximum allowed instructions.
        Raises:
            InstructionLimitExceeded: If the number of executed instructions exceeds the maximum allowed.
        """
        self._instruction_count += 1
        if self._instruction_count > self.max_instructions:
            raise InstructionLimitExceeded

    def _api(self, command: _Command, name: str, value: Any, action: Any) -> None:
        """Executes an API action and logs the result, handling any runtime errors that may occur.

        Args:
            command (_Command): The command being executed, used for logging the line number.
            name (str): Name of the API action being executed, used for logging.
            value (Any): Value associated with the API action, used for logging.
            action (Any): The callable action to be executed, which may raise a RuntimeErrorCode.
        Raises:
            RuntimeErrorCode: If an error occurs during the execution of the API action.
        """
        try:
            action()
        except RuntimeErrorCode:
            self._api_error = (name, value)
            raise
        self.log.record(command.line, name, *("" if value is None else (value,)))

    def _evaluate_calculated(self, tokens: list[str]) -> Any:
        """Evaluates a calculated expression represented by a list of tokens."""
        if len(tokens) == 1:
            return self._evaluate(tokens[0])
        if len(tokens) == 2 and tokens[0] == "not":
            value = self._evaluate(tokens[1])
            if not isinstance(value, bool):
                raise RuntimeErrorCode("E_BAD_OPERAND")
            return not value
        if len(tokens) == 3:
            left = self._evaluate(tokens[0])
            self._validate_first_operand(tokens[1], left)
            right = self._evaluate(tokens[2])
            return self._binary(tokens[1], left, right)
        if len(tokens) == 2 and tokens[0] == "isThere":
            return self._is_there(tokens[1])
        raise RuntimeErrorCode("E_BAD_ARG")

    def _evaluate(self, token: str) -> Any:
        """Evaluates a single token, returning its corresponding value."""
        if token == "true":
            return True
        if token == "false":
            return False
        if token.isdigit():
            return int(token)
        if token == "isThere":
            raise RuntimeErrorCode("E_BAD_ARG")
        if token in self.variables:
            return self.variables[token]
        raise RuntimeErrorCode("E_UNINITIALIZED")

    def _is_there(self, token: str) -> bool:
        """Evaluates the 'isThere' command, checking if a specific kind of object is present in front of the robot."""
        self._api_error = ("isThere", None)
        value = self._evaluate(token)
        if not isinstance(value, int) or isinstance(value, bool):
            self._api_error = ("isThere", value)
            raise RuntimeErrorCode("E_BAD_ARG")
        try:
            result = self.robot.is_there(value)
        except RuntimeErrorCode:
            self._api_error = ("isThere", value)
            raise
        self.log.record(self._current_line, "isThere", value, result)
        return result

    @staticmethod
    def _require_int(value: Any, code: str) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise RuntimeErrorCode(code)

    @classmethod
    def _validate_first_operand(cls, operator: str, value: Any) -> None:
        if operator in {"+", "-", "*", "<", "<=", ">", ">="}:
            cls._require_int(value, "E_BAD_OPERAND")
        elif operator in {"and", "or"} and not isinstance(value, bool):
            raise RuntimeErrorCode("E_BAD_OPERAND")

    def _binary(self, operator: str, left: Any, right: Any) -> Any:
        """Evaluates a binary operation between two operands, checking for type compatibility and returning the result.

        Args:
            operator (str): The binary operator to be applied (e.g., "+", "-", "*", "and", "or", "=", "<>", etc.).
            left (Any): The left operand of the binary operation.
            right (Any): The right operand of the binary operation.

        Raises:
            RuntimeErrorCode: If the operands are of incompatible types for the given operator, or if the operator is not recognized.

        Returns:
            Any: The result of the binary operation, which can be an integer or boolean depending on the operator and operands.
        """
        if operator in {"+", "-", "*", "<", "<=", ">", ">="}:
            self._require_int(left, "E_BAD_OPERAND")
            self._require_int(right, "E_BAD_OPERAND")
            return {
                "+": lambda: left + right,
                "-": lambda: left - right,
                "*": lambda: left * right,
                "<": lambda: left < right,
                "<=": lambda: left <= right,
                ">": lambda: left > right,
                ">=": lambda: left >= right,
            }[operator]()

        if operator in {"and", "or"}:
            if not isinstance(left, bool) or not isinstance(right, bool):
                raise RuntimeErrorCode("E_BAD_OPERAND")
            return left and right if operator == "and" else left or right
        if operator in {"=", "<>"}:
            if type(left) is not type(right):
                raise RuntimeErrorCode("E_BAD_OPERAND")
            return left == right if operator == "=" else left != right
        raise RuntimeErrorCode("E_BAD_ARG")


def _parse(source: str) -> list[_Command]:
    """Parses the source code into a list of commands, handling indentation and block structures.

    Args:
        source (str): The source code to be parsed into commands.

    Returns:
        list[_Command]: A list of _Command objects representing the parsed commands, including their line numbers, tokens, and any nested blocks for control structures.
    """
    lines = [
        (number, len(text) - len(text.lstrip(" ")), text.strip().split(" "))
        for number, text in enumerate(source.splitlines(), 1)
        if text.strip()
    ]

    def block(index: int, indent: int) -> tuple[list[_Command], int]:
        result: list[_Command] = []
        while index < len(lines) and lines[index][1] == indent:
            line, _, tokens = lines[index]
            command = _Command(line, tokens)
            index += 1
            if (
                tokens[0] in {"if", "while"}
                and index < len(lines)
                and lines[index][1] > indent
            ):
                command.body, index = block(index, lines[index][1])
            if (
                tokens[0] == "if"
                and index < len(lines)
                and lines[index][1] == indent
                and lines[index][2][0] == "else"
            ):
                command.else_line = lines[index][0]
                index += 1
                if index < len(lines) and lines[index][1] > indent:
                    command.otherwise, index = block(index, lines[index][1])
            result.append(command)
        return result, index

    return block(0, lines[0][1] if lines else 0)[0]
