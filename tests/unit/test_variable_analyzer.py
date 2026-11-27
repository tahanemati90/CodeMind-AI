from codemind.analyzers.static.variable_analyzer import UndefinedVariableAnalyzer


def test_reports_undefined_variable() -> None:
    analyzer = UndefinedVariableAnalyzer()
    source = "print(x)\n"
    diagnostics = analyzer.analyze(source)
    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM001"
    assert "x" in diagnostics[0].message


def test_knows_builtin_names() -> None:
    analyzer = UndefinedVariableAnalyzer()
    source = "print('hello')\n"
    diagnostics = analyzer.analyze(source)
    assert len(diagnostics) == 0


def test_does_not_report_variable_defined_in_scope() -> None:
    analyzer = UndefinedVariableAnalyzer()
    # در اینجا x داخل تابع تعریف شده، اما تحلیلگرِ فعلی فقط اسکوپ سراسری را می‌بیند
    source = "def func():\n    x = 10\n    print(x)\n"
    diagnostics = analyzer.analyze(source)
    assert len(diagnostics) == 0


def test_reports_undefined_if_used_before_definition_in_scope() -> None:
    analyzer = UndefinedVariableAnalyzer()
    # اینجا x قبل از اینکه تعریف شود، چاپ شده.
    # الان احتمالاً تحلیلگر چون در کل اسکوپ x را می‌بیند، فکر می‌کند همه چیز درست است!
    source = "def func():\n    print(x)\n    x = 10\n"
    diagnostics = analyzer.analyze(source)
    assert len(diagnostics) == 1, "باید خطا بدهد چون x قبل از تعریف استفاده شده!"
