class UnknownError(Exception):
    """Exception to signal an unknown error."""

    exit_code = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
