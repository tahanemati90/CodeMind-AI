from codemind.analyzers.static import UndefinedVariableAnalyzer, UnusedImportAnalyzer
from codemind.diagnostics import Diagnostic


class AnalysisEngine:
    """موتور اصلی برای اجرای تمام تحلیلگرهای ثبت‌شده."""

    def __init__(self) -> None:
        self.analyzers = [
            UndefinedVariableAnalyzer(),
            UnusedImportAnalyzer(),
        ]

    def analyze_source(self, source: str, filename: str = "main.py") -> list[Diagnostic]:
        all_diagnostics: list[Diagnostic] = []

        for analyzer in self.analyzers:
            all_diagnostics.extend(analyzer.analyze(source, filename))

        return sorted(all_diagnostics, key=lambda d: (d.line or 0, d.column or 0))
