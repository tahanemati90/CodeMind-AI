from codemind.analyzers.static.logical_analyzer import LogicalAnalyzer


def test_reports_division_by_zero() -> None:
    analyzer = LogicalAnalyzer()
    source = "x = 10 / 0\n"
    diagnostics = analyzer.analyze(source)
    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM002"
    assert "division by zero" in diagnostics[0].message.lower()


def test_reports_improper_none_comparison() -> None:
    analyzer = LogicalAnalyzer()
    source = "if x == None: pass\n"
    diagnostics = analyzer.analyze(source)
    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM003"


def test_reports_constant_condition() -> None:
    analyzer = LogicalAnalyzer()
    source = "if True:\n    pass\n"
    diagnostics = analyzer.analyze(source)
    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM004"


def test_reports_while_true_without_break() -> None:
    analyzer = LogicalAnalyzer()
    source = "while True:\n    do_work()\n"
    diagnostics = analyzer.analyze(source)
    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM005"


def test_does_not_report_while_true_with_break() -> None:
    analyzer = LogicalAnalyzer()
    source = "while True:\n    if done:\n        break\n"
    diagnostics = analyzer.analyze(source)
    assert diagnostics == []


def test_does_not_report_variable_while_condition() -> None:
    analyzer = LogicalAnalyzer()
    source = "while running:\n    do_work()\n"
    diagnostics = analyzer.analyze(source)
    assert diagnostics == []


def test_reports_out_of_range_literal_list_index() -> None:
    diagnostics = LogicalAnalyzer().analyze("value = [10, 20][2]\n")
    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM006"


def test_reports_out_of_range_negative_tuple_index() -> None:
    diagnostics = LogicalAnalyzer().analyze("value = (10, 20)[-3]\n")
    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM006"


def test_reports_out_of_range_string_index() -> None:
    diagnostics = LogicalAnalyzer().analyze('value = "abc"[3]\n')
    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM006"


def test_accepts_valid_positive_and_negative_literal_indexes() -> None:
    source = 'a = [10, 20][1]\nb = [10, 20][-2]\nc = "ab"[-1]\n'
    assert LogicalAnalyzer().analyze(source) == []


def test_does_not_report_dynamic_or_boolean_indexes() -> None:
    source = "a = items[0]\nb = [10, 20][index]\nc = [10][True]\n"
    assert LogicalAnalyzer().analyze(source) == []


def test_reports_incomplete_return_path() -> None:
    analyzer = LogicalAnalyzer()
    source = """
def my_func(x):
    if x > 0:
        return x
"""
    diagnostics = analyzer.analyze(source)
    cm007_errors = [d for d in diagnostics if d.rule_id == "CM007"]
    assert len(cm007_errors) >= 1
    assert "return" in cm007_errors[0].message.lower()


def test_accepts_complete_return_path() -> None:
    analyzer = LogicalAnalyzer()
    source = """
def my_func(x):
    if x > 0:
        return x
    return 0
"""
    diagnostics = analyzer.analyze(source)
    assert not any(d.rule_id == "CM007" for d in diagnostics)
