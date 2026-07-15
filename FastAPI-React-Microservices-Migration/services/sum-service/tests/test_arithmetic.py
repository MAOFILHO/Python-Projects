from app.arithmetic import my_sum


def test_no_args_returns_zero():
    assert my_sum() == 0


def test_one_value():
    assert my_sum(5) == 5


def test_many_values():
    assert my_sum(1, 2, 3, 4, 5) == 15


def test_negatives():
    assert my_sum(-1, -2, 3) == 0


def test_floats():
    assert my_sum(1.5, 2.5) == 4.0
