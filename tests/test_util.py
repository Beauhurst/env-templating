from env_templating.util import confirm


def test_confirm_yes_response(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    assert confirm("Are you sure?", default=True)


def test_confirm_no_response(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    assert not confirm("Are you sure?", default=True)


def test_confirm_default_true(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: '')
    assert confirm("Are you sure?", default=True)


def test_confirm_default_false(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: '')
    assert not confirm("Are you sure?", default=False)


def test_confirm_invalid_then_yes(monkeypatch):
    inputs = iter(['maybe', 'y'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    assert confirm("Are you sure?", default=True)


def test_confirm_invalid_then_no(monkeypatch):
    inputs = iter(['maybe', 'n'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    assert not confirm("Are you sure?", default=True)
