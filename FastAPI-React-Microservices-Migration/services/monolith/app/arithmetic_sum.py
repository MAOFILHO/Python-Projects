"""Duplicated (intentionally, not imported from sum-service) recursive sum."""


def my_sum(*args: float) -> float:
    if args:
        return args[0] + my_sum(*args[1:])
    return 0
