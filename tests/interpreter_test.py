import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from interpreter import DummyRobot, Interpreter  # noqa: E402


@pytest.fixture
def run_program():
    def run(map_rows: list[str], source: str, **kwargs: object):
        robot = DummyRobot.from_map(map_rows)
        log = Interpreter(robot, **kwargs).run(source) #type: ignore
        return robot, log.lines

    return run

@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2 + 3", "5"),
        ("5 - 2", "3"),
        ("2 * 3", "6"),
        ("2 < 3", "true"),
        ("2 <= 2", "true"),
        ("3 > 2", "true"),
        ("3 >= 3", "true"),
        ("2 = 2", "true"),
        ("2 <> 3", "true"),
        ("true and false", "false"),
        ("true or false", "true"),
        ("not false", "true"),
    ],
)
def test_expressions(run_program, expression: str, expected: str):
    _, lines = run_program([">"], f"set result to {expression}\nprint result")

    assert lines == (f"2 print {expected}", "EOR")

@pytest.mark.parametrize(
    ("wrong_expression",),
    [
        ("2 + true",),
        ("false - 1",),
        ("2 * false",),
        ("true < 1",),
        ("false <= 1",),
        ("1 > true",),
        ("1 >= false",),
        ("true = 1",),
        ("false <> 1",),
        ("true and 1",),
        ("false or 1",),
        ("not 1",),
    ],
)
def test_expression_with_bad_operand(run_program,wrong_expression: str):
    _, lines1 = run_program([">"], f"set result to {wrong_expression}\nprint result")
    assert lines1 == ("1 E_BAD_OPERAND", "EOR")

def test_special_equalities(run_program):
    _, lines_true = run_program([">"], "set result to 1 = 1\nprint result\nset result to 1 <> 2\nprint result\nset result to true = true\nprint result\nset result to false <> true\nprint result")

    assert lines_true == (
        "2 print true",
        "4 print true",
        "6 print true",
        "8 print true",
        "EOR",
    )

    _, lines_false = run_program([">"], "set result to 1 = 2\nprint result\nset result to 1 <> 1\nprint result\nset result to true = false\nprint result\nset result to false <> false\nprint result")

    assert lines_false == (
        "2 print false",
        "4 print false",
        "6 print false",
        "8 print false",
        "EOR",
    )

def test_empty_program_finishes_with_eor(run_program):
    _, lines = run_program([">"], "")

    assert lines == ("EOR",)

def test_is_there_and_print_are_logged(run_program):
    _, lines = run_program(
        [">@."],
        "set gold to isThere 2\nprint gold",
    )

    assert lines == (
        "1 isThere 2 true",
        "2 print true",
        "EOR",
    )

def test_if_else_executes_only_the_selected_branch(run_program):
    _, lines = run_program(
        [">.."],
        "if false\n  print 1\nelse\n  print 2",
    )

    assert lines == ("1", "3", "4 print 2", "EOR")

def test_robot_moves_turns_and_mines(run_program):
    robot, lines = run_program(
        [">@."],
        "step forward 1\nturn by 1\nturn by 3\nmine here",
    )

    assert (robot.row, robot.column, robot.direction) == (0, 1, ">")
    assert robot.mined == 1
    assert lines == (
        "1 step forward 1",
        "2 turn by 1",
        "3 turn by 3",
        "4 mine here",
        "EOR",
    )

def test_runtime_error_stops_program_and_is_logged(run_program):
    _, lines = run_program(
        [">.."],
        "step forward 5\nprint 1",
    )

    assert lines == ("1 step forward 5 E_BEDROCK_HIT", "EOR")

def test_type_mismatch_is_reported(run_program):
    _, lines = run_program(
        [">"],
        "set value to 1\nset value to false\nprint 1",
    )

    assert lines == ("2 E_TYPE_MISMATCH", "EOR")

def test_binary_expression_checks_left_operand_before_reading_right_operand(run_program):
    _, lines = run_program(
        [">"],
        "set value to true + missing",
    )

    assert lines == ("1 E_BAD_OPERAND", "EOR")

def test_instruction_limit_does_not_write_eor(run_program):
    _, lines = run_program(
        [">"],
        "while true\n  turn by 0",
        max_instructions=3,
    )

    assert lines == (
        "1",
        "2 turn by 0",
        "1",
        "INSTRUCTION_COUNT_LIMIT_EXCEEDED",
    )
    assert "EOR" not in lines

def test_each_run_starts_with_fresh_state():
    robot = DummyRobot.from_map([">"])
    interpreter = Interpreter(robot)

    first = interpreter.run("set value to 1")
    second = interpreter.run("print value")

    assert first.lines == ("EOR",)
    assert second.lines == ("1 E_UNINITIALIZED", "EOR")

def test_log_can_be_written_to_a_file():
    robot = DummyRobot.from_map([">"])
    log = Interpreter(robot).run("print false")

    with TemporaryDirectory() as directory:
        output = Path(directory) / "output.txt"
        log.write(output)
        assert output.read_text(encoding="utf-8") == "1 print false\nEOR\n"

@pytest.mark.parametrize(
    ("expression","error_code"),
    [

        ("step forward true","E_BAD_ARG"),
        ("turn by false","E_BAD_ARG"),
        ("mine here", "E_NO_GOLD"),
        ("step forward 1", "E_BEDROCK_HIT"),
    ],
)
def test_api_argument_failures(run_program,expression: str,error_code: str):
    _, lines = run_program([">"], expression)
    assert lines == (f"1 {expression} {error_code}", "EOR")

def test_state_snapshots():
    robot = DummyRobot.from_map([">"])

    interpreter = Interpreter(robot)
    interpreter.run("set value to 1\nprint value")
    assert len(interpreter.state_snapshots) == 2
    assert interpreter.state_snapshots[0].variables == {"value": 1}
    assert interpreter.state_snapshots[0].line_number == 1
    assert interpreter.state_snapshots[0].robot_position == (0, 0)
    assert interpreter.state_snapshots[0].robot_direction == ">"

    assert interpreter.state_snapshots[1].variables == {"value": 1}
    assert interpreter.state_snapshots[1].line_number == 2
    assert interpreter.state_snapshots[1].robot_position == (0, 0)
    assert interpreter.state_snapshots[1].robot_direction == ">"

def test_state_snapshots_are_recorded_once_for_api_commands():
    robot = DummyRobot.from_map([">."])

    interpreter = Interpreter(robot)
    interpreter.run("step forward 1\nturn by 1\nprint false")

    assert len(interpreter.state_snapshots) == 3
    assert [snapshot.line_number for snapshot in interpreter.state_snapshots] == [1, 2, 3]
    assert interpreter.state_snapshots[0].robot_position == (0, 1)
    assert interpreter.state_snapshots[1].robot_direction == "^"

def test_state_snapshots_are_cleared_between_runs():
    robot = DummyRobot.from_map([">"])

    interpreter = Interpreter(robot)
    interpreter.run("set value to 1\nprint value")
    interpreter.run("set other to 2\nprint other\nset value to 3\nturn by 1")

    assert len(interpreter.state_snapshots) == 4
    assert interpreter.state_snapshots[0].variables == {"other": 2}
    assert interpreter.state_snapshots[1].variables == {"other": 2}
    assert interpreter.state_snapshots[2].variables == {"other": 2, "value": 3}
    assert interpreter.state_snapshots[3].variables == {"other": 2, "value": 3}
    assert interpreter.state_snapshots[0].line_number == 1
    assert interpreter.state_snapshots[1].line_number == 2
    assert interpreter.state_snapshots[2].line_number == 3
    assert interpreter.state_snapshots[3].line_number == 4
    assert interpreter.state_snapshots[0].robot_position == (0, 0)
    assert interpreter.state_snapshots[1].robot_position == (0, 0)
    assert interpreter.state_snapshots[2].robot_position == (0, 0)
    assert interpreter.state_snapshots[3].robot_position == (0, 0)
    assert interpreter.state_snapshots[0].robot_direction == ">"
    assert interpreter.state_snapshots[1].robot_direction == ">"
    assert interpreter.state_snapshots[2].robot_direction == ">"
    assert interpreter.state_snapshots[3].robot_direction == "^"

def test_entry_snapshots_capture_state_before_each_statement():
    robot = DummyRobot.from_map([">."])
    interpreter = Interpreter(robot)
    interpreter.run("set value to 1\nstep forward 1\nprint value")

    assert [snapshot.line_number for snapshot in interpreter.entry_snapshots] == [1, 2, 3]
    assert interpreter.entry_snapshots[0].variables == {}
    assert interpreter.entry_snapshots[0].robot_position == (0, 0)
    assert interpreter.entry_snapshots[1].variables == {"value": 1}
    assert interpreter.entry_snapshots[1].robot_position == (0, 0)
    assert interpreter.entry_snapshots[2].robot_position == (0, 1)

def test_entry_snapshot_is_recorded_when_statement_fails():
    robot = DummyRobot.from_map([">"])
    interpreter = Interpreter(robot)
    interpreter.run("step forward 1")

    assert len(interpreter.entry_snapshots) == 1
    assert interpreter.entry_snapshots[0].line_number == 1
    assert interpreter.entry_snapshots[0].robot_position == (0, 0)

def test_entry_snapshots_record_log_positions():
    robot = DummyRobot.from_map([">"])
    interpreter = Interpreter(robot)
    log = interpreter.run("set value to 1\nprint value")

    assert interpreter.entry_log_indices == [0, 0]
    assert log.lines == ("2 print 1", "EOR")
