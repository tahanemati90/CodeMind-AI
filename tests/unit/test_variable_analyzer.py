from codemind.analyzers.static import UndefinedVariableAnalyzer
from codemind.diagnostics import Severity


def test_detects_undefined_variable() -> None:
    diagnostics = UndefinedVariableAnalyzer().analyze("print(total)")

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM001"
    assert diagnostics[0].severity == Severity.WARNING
    assert diagnostics[0].line == 1
    assert diagnostics[0].column == 7


def test_does_not_report_defined_variable() -> None:
    source = "total = 10\nprint(total)"

    assert UndefinedVariableAnalyzer().analyze(source) == []


def test_does_not_report_builtin_name() -> None:
    assert UndefinedVariableAnalyzer().analyze("print(len([1, 2]))") == []


def test_reports_syntax_error_without_crashing() -> None:
    diagnostics = UndefinedVariableAnalyzer().analyze("if True print('hello')")

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "CM000"
    assert diagnostics[0].category == "syntax"
    assert diagnostics[0].severity == Severity.ERROR


def test_reports_same_undefined_name_once() -> None:
    diagnostics = UndefinedVariableAnalyzer().analyze(
        "print(score)\nprint(score)"
    )

    assert len(diagnostics) == 1
    assert "score" in diagnostics[0].message
