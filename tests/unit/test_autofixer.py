from codemind.diagnostics.autofixer import AutoFixer


def test_autofixer_zero_division() -> None:
    fixer = AutoFixer()
    fixed_code = fixer.fix("10 / 0", "CM002")
    assert "try:" in fixed_code
    assert "except ZeroDivisionError:" in fixed_code
