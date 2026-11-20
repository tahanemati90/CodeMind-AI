from codemind.engine import AnalysisEngine


def test_engine_finds_multiple_issues() -> None:
    engine = AnalysisEngine()
    source = """
x = 10
print(y)  # y تعریف نشده
z = x + a  # a تعریف نشده
"""
    results = engine.analyze_source(source)
    
    # باید دو خطای متغیر تعریف‌نشده پیدا کند (y و a)
    # print جزو built-in هاست و نباید خطا بگیرد
    
    assert len(results) == 2
    names_found = [r.message for r in results]
    assert any("«y»" in msg for msg in names_found)
    assert any("«a»" in msg for msg in names_found)
