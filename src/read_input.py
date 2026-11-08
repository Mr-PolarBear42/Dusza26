from pathlib import Path


_MAP_SYMBOLS = frozenset(".#@^>v<")


def read_input(file_path: str | Path):
    with open(file_path, "r", encoding="utf-8") as fs:
        dimensions = fs.readline().split()
        if len(dimensions) != 2:
            raise ValueError("The first line must contain the map height and width")

        try:
            h, w = (int(value) for value in dimensions)
        except ValueError as error:
            raise ValueError("The map dimensions must be integers") from error
        if h <= 0 or w <= 0:
            raise ValueError("The map dimensions must be positive")

        map_data: list[list[str]] = []
        for y in range(h):
            line = fs.readline()
            if not line:
                raise ValueError(f"Map row {y + 1} is missing")
            line = line.rstrip("\r\n")
            if len(line) != w:
                raise ValueError(
                    f"Map row {y + 1} must contain exactly {w} characters"
                )
            invalid_symbols = set(line) - _MAP_SYMBOLS
            if invalid_symbols:
                invalid = ", ".join(sorted(invalid_symbols))
                raise ValueError(f"Map row {y + 1} contains invalid symbols: {invalid}")
            map_data.append(list(line))

        return map_data, w, h, fs.read()
