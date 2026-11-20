from codemind.engine import AnalysisEngine


def test_engine_finds_multiple_issues() -> None:
    engine = AnalysisEngine()
    source = """
x = 10
print(y)
z = x + a
"""
    results = engine.analyze_source(source)

    assert len(results) == 2
    messages = [r.message for r in results]
    assert any("«y»" in msg for msg in messages)
    assert any("«a»" in msg for msg in messages)


def test_engine_combines_analyzers_and_sorts_by_line() -> None:
    engine = AnalysisEngine()
    source = "import os\nprint(missing)\n"
    results = engine.analyze_source(source)

    rule_ids = [r.rule_id for r in results]
    assert "CM002" in rule_ids
    assert "CM001" in rule_ids
    assert results == sorted(results, key=lambda d: (d.line or 0, d.column or 0))
