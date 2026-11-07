from pathlib import Path


class ExecutionLog:
    def __init__(self) -> None:
        self._lines: list[str] = []

    def record(
        self,
        line_number: int,
        api: str | None = None,
        *details: object,
        error: str | None = None,
    ) -> None:
        fields = [str(line_number)]
        if api is not None:
            fields.append(api)
        fields.extend(_format_value(value) for value in details)
        if error is not None:
            fields.append(error)
        self._lines.append(" ".join(fields))

    def add_limit_error(self) -> None:
        self._lines.append("INSTRUCTION_COUNT_LIMIT_EXCEEDED")

    def finish(self) -> None:
        self._lines.append("EOR")

    def write(self, path: str | Path) -> None:
        Path(path).write_text("\n".join(self._lines) + "\n", encoding="utf-8")

    @property
    def lines(self) -> tuple[str, ...]:
        return tuple(self._lines)


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
