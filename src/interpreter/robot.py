from dataclasses import dataclass, field

from .errors import RuntimeErrorCode


@dataclass
class Robot:
    grid: list[list[str]]
    row: int
    column: int
    direction: str
    mined: int = 0
    mined_positions: set[tuple[int, int]] = field(default_factory=set)
    discovered: set[tuple[int, int]] = field(default_factory=set)
    DIRECTIONS = {"^": (-1, 0), ">": (0, 1), "v": (1, 0), "<": (0, -1)}
    
    
    
    @classmethod
    def from_map(cls, grid: list[str]) -> Robot:
        copied = [list(row) for row in grid]
        robot: tuple[int, int, str] | None = None
        for row, values in enumerate(copied):
            for column, value in enumerate(values):
                if value in cls.DIRECTIONS:
                    if robot is not None:
                        raise ValueError("map contains more than one robot")
                    robot = (row, column, value)
                    values[column] = "."
        if robot is None:
            raise ValueError("map does not contain a robot")
        row, column, direction = robot
        discovered = {(row, column)}
        return cls(copied, row, column, direction,discovered=discovered)

    def is_there(self, kind: int) -> bool:
        if kind not in (0, 1, 2):
            raise RuntimeErrorCode("E_BAD_ARG")
        target = self._front()
        if not self._in_bounds(*target[:2]):
            return kind == 1
        self.discovered.add((target[0], target[1]))
        if self.grid[target[0]][target[1]] == "#":
            return kind == 1
        return (kind == 2 and self.grid[target[0]][target[1]] == "@") or (
            kind == 0 and self.grid[target[0]][target[1]] == "."
        )

    def step_forward(self, distance: int) -> None:
        if not isinstance(distance, int) or isinstance(distance, bool) or distance < 0:
            raise RuntimeErrorCode("E_BAD_ARG")
        for _ in range(distance):
            target = self._front()
            if (
                not self._in_bounds(*target[:2])
                or self.grid[target[0]][target[1]] == "#"
            ):
                raise RuntimeErrorCode("E_BEDROCK_HIT")
            self.row, self.column = target[:2]
            self.discovered.add((self.row, self.column))

    def turn_by(self, quarter_turns: int) -> None:
        if (
            not isinstance(quarter_turns, int)
            or isinstance(quarter_turns, bool)
            or quarter_turns < 0
        ):
            raise RuntimeErrorCode("E_BAD_ARG")
        directions = "^>v<"
        self.direction = directions[
            (directions.index(self.direction) - quarter_turns) % 4
        ]

    def mine_here(self) -> None:
        if self.grid[self.row][self.column] != "@":
            raise RuntimeErrorCode("E_NO_GOLD")
        self.grid[self.row][self.column] = "."
        self.mined += 1
        self.mined_positions.add((self.row, self.column))

    def _front(self) -> tuple[int, int, str]:
        delta_row, delta_column = self.DIRECTIONS[self.direction]
        row, column = self.row + delta_row, self.column + delta_column
        if not self._in_bounds(row, column):
            return row, column, "#"
        return row, column, self.grid[row][column]

    def _in_bounds(self, row: int, column: int) -> bool:
        return 0 <= row < len(self.grid) and 0 <= column < len(self.grid[row])
