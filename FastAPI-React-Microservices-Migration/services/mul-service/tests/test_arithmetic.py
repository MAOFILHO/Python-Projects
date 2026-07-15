from app.arithmetic import my_mul


def test_no_args_returns_one():
    assert my_mul() == 1


def test_one_value():
    assert my_mul(5) == 5


def test_many_values():
    assert my_mul(1, 2, 3, 4) == 24


def test_negatives():
    assert my_mul(-1, -2, 3) == 6


def test_floats():
    assert my_mul(1.5, 2.0) == 3.0
