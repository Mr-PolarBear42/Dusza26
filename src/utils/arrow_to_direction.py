def arrow_to_direction(arrow: str) -> str:
    """Converts an arrow symbol to a direction string.

    Args:
        arrow (str): The arrow symbol to be converted.

    Returns:
        str: The corresponding direction string.

    Raises:
        ValueError: If the provided arrow symbol is invalid.
    """
    arrow_mapping = {
        "^": "North",
        "v": "South",
        "<": "West",
        ">": "East",
    }

    if arrow not in arrow_mapping:
        raise ValueError(f"Invalid arrow symbol: {arrow}")

    return arrow_mapping[arrow]
