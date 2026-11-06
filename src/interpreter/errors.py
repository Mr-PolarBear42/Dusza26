class RuntimeErrorCode(Exception):
    """A MineScript runtime failure carrying the required log error code."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class InstructionLimitExceeded(Exception):
    pass


class ProgramTerminated(Exception):
    pass
