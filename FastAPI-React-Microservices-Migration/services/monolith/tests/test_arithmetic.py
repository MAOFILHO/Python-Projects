from app.arithmetic_mul import my_mul
from app.arithmetic_sum import my_sum


def test_sum_no_args_returns_zero():
    assert my_sum() == 0


def test_sum_many_values():
    assert my_sum(1, 2, 3, 4, 5) == 15


def test_sum_negatives():
    assert my_sum(-1, -2, 3) == 0


def test_mul_no_args_returns_one():
    assert my_mul() == 1


def test_mul_many_values():
    assert my_mul(1, 2, 3, 4) == 24


def test_mul_negatives():
    assert my_mul(-1, -2, 3) == 6
