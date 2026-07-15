"""Pure recursive product, ported from the original monolith's app/lib/arithmetic/mul.py."""


def my_mul(*args: float) -> float:
    if args:
        return args[0] * my_mul(*args[1:])
    return 1
