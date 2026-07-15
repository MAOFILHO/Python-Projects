"""Duplicated (intentionally, not imported from mul-service) recursive product."""


def my_mul(*args: float) -> float:
    if args:
        return args[0] * my_mul(*args[1:])
    return 1
