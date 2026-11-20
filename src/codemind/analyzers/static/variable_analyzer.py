import ast
import builtins

from codemind.diagnostics import Diagnostic, Severity

# استخراج دقیق تمام نام‌های توکار پایتون
_BUILTIN_NAMES = set(dir(builtins))


class _ScopeVisitor(ast.NodeVisitor):
    """جمع‌آوری تعاریف و استفاده‌ها در یک محدوده مشخص."""

    def __init__(self) -> None:
        self.defined: set[str] = set()
        self.used: list[ast.Name] = []

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.defined.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.used.append(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.defined.add(node.name)
        # فعلاً وارد بدنه تابع نمی‌شویم تا تحلیل scope پیچیده نشود
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.defined.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.defined.add(node.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.defined.add(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name != "*":
                self.defined.add(alias.asname or alias.name)


class UndefinedVariableAnalyzer:
    """پیدا کردن متغیرهایی که قبل از تعریف، استفاده شده‌اند."""

    rule_id = "CM001"

    def analyze(self, source: str, filename: str = "<memory>") -> list[Diagnostic]:
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as error:
            return [
                Diagnostic(
                    rule_id="CM000",
                    severity=Severity.ERROR,
                    category="syntax",
                    message=error.msg,
                    file=filename,
                    line=error.lineno,
                    column=error.offset,
                    confidence=1.0,
                    source="python.ast",
                    suggestion="خطای نحوی را اصلاح کنید.",
                )
            ]

        visitor = _ScopeVisitor()
        visitor.visit(tree)

        diagnostics: list[Diagnostic] = []
        reported: set[str] = set()

        for name_node in visitor.used:
            name = name_node.id
            if (
                name not in visitor.defined
                and name not in _BUILTIN_NAMES
                and name not in reported
            ):
                reported.add(name)
                msg = f"نام «{name}» استفاده شده اما تعریف نشده است."
                sug = f"بررسی کنید «{name}» درست تایپ شده باشد."
                
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        severity=Severity.WARNING,
                        category="undefined-name",
                        message=msg,
                        file=filename,
                        line=name_node.lineno,
                        column=name_node.col_offset + 1,
                        confidence=0.85,
                        source="ast",
                        suggestion=sug,
                    )
                )

        return diagnostics
