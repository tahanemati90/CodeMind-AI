from codemind.analyzers.static import UndefinedVariableAnalyzer
from codemind.diagnostics import Diagnostic


class AnalysisEngine:
    """موتور اصلی برای اجرای تمام تحلیلگرهای ثبت شده."""

    def __init__(self) -> None:
        # فعلاً فقط همین یک تحلیلگر را داریم، بعداً لیست را گسترش می‌دهیم
        self.analyzers = [
            UndefinedVariableAnalyzer(),
        ]

    def analyze_source(self, source: str, filename: str = "main.py") -> list[Diagnostic]:
        """اجرای تمام تحلیلگرها روی کد ورودی."""
        all_diagnostics = []
        
        for analyzer in self.analyzers:
            results = analyzer.analyze(source, filename)
            all_diagnostics.extend(results)
            
        # مرتب‌سازی بر اساس شماره خط
        return sorted(all_diagnostics, key=lambda d: (d.line or 0, d.column or 0))
