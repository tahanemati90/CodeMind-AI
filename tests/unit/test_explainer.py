from codemind.diagnostics.explainer import DiagnosticExplainer


def test_explainer_zero_division() -> None:
    explainer = DiagnosticExplainer()
    explanation = explainer.explain("ZeroDivisionError: division by zero")
    assert explanation.error_type == "ZeroDivisionError"
    assert "صفر" in explanation.friendly_message
    assert explanation.patch_snippet is not None


def test_explainer_syntax_error() -> None:
    explainer = DiagnosticExplainer()
    explanation = explainer.explain("SyntaxError: invalid syntax")
    assert explanation.error_type == "SyntaxError"
    assert "نگارشی" in explanation.friendly_message


def test_explainer_unknown() -> None:
    explainer = DiagnosticExplainer()
    explanation = explainer.explain("SomeRandomError")
    assert explanation.error_type == "UnknownError"
