from antislapp.pages import debug


def test_nothing():
    p = debug.Debug()
    assert isinstance(p, debug.Debug)