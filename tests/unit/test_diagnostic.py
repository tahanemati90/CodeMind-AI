import pytest

from codemind.diagnostics import Diagnostic, Severity


def test_diagnostic_creation():
    diagnostic = Diagnostic(
        rule_id="PY001",
        severity=Severity.ERROR,
        category="syntax",
        message="Invalid syntax",
        file="main.py",
        line=12,
        column=5,
        confidence=1.0,
        source="parser",
    )

    assert diagnostic.rule_id == "PY001"
    assert diagnostic.severity == Severity.ERROR
    assert diagnostic.line == 12


def test_diagnostic_serialization():
    diagnostic = Diagnostic(
        rule_id="PY002",
        severity=Severity.WARNING,
        category="logic",
        message="Possible logical issue",
        file="main.py",
        line=8,
        column=3,
        confidence=0.85,
        source="logic_analyzer",
    )

    result = diagnostic.to_dict()

    assert result["severity"] == "warning"
    assert result["confidence"] == 0.85
    assert result["rule_id"] == "PY002"


def test_invalid_confidence():
    with pytest.raises(ValueError):
        Diagnostic(
            rule_id="PY003",
            severity=Severity.ERROR,
            category="test",
            message="Test error",
            file="main.py",
            line=1,
            column=1,
            confidence=1.5,
            source="test",
        )


def test_invalid_line():
    with pytest.raises(ValueError):
        Diagnostic(
            rule_id="PY004",
            severity=Severity.ERROR,
            category="test",
            message="Test error",
            file="main.py",
            line=0,
            column=1,
            confidence=1.0,
            source="test",
        )
