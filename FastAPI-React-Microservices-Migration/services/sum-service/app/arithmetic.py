"""Pure recursive sum, ported from the original monolith's app/lib/arithmetic/sum.py."""


def my_sum(*args: float) -> float:
    if args:
        return args[0] + my_sum(*args[1:])
    return 0
