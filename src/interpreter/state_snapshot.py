class StateSnapshot:
    """
    A snapshot of the interpreter state at a given point in time.
    """

    def __init__(
        self,
        variables: dict,
        line_number: int,
        robot_position: tuple[int, int],
        robot_direction: str,
        mined_positions: set[tuple[int, int]] | None = None,
    ):
        self.variables = variables
        self.line_number = line_number
        self.robot_position = robot_position
        self.robot_direction = robot_direction
        self.mined_positions = frozenset(mined_positions or ())

    def __repr__(self):
        return f"StateSnapshot(variables={self.variables}, line_number={self.line_number}, robot_position={self.robot_position}, robot_direction={self.robot_direction})"
