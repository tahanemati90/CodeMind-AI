import ast

from codemind.diagnostics import Diagnostic, Severity


class _ImportCollector(ast.NodeVisitor):
    """Collect imported names and every name loaded anywhere in the module."""

    def __init__(self) -> None:
        self.imports: dict[str, ast.Import | ast.ImportFrom] = {}
        self.used: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            bound = alias.asname or alias.name.split(".")[0]
            self.imports.setdefault(bound, node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == "*":
                continue
            bound = alias.asname or alias.name
            self.imports.setdefault(bound, node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.used.add(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # for "import os.path" style access, the root name is what matters
        self.generic_visit(node)


class UnusedImportAnalyzer:
    """Report imported names that are never referenced in the module."""

    rule_id = "CM002"

    def analyze(self, source: str, filename: str = "<memory>") -> list[Diagnostic]:
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError:
            # syntax errors are reported by the syntax/name analyzer, not here
            return []

        collector = _ImportCollector()
        collector.visit(tree)

        diagnostics: list[Diagnostic] = []
        for name, node in collector.imports.items():
            if name in collector.used:
                continue
            diagnostics.append(
                Diagnostic(
                    rule_id=self.rule_id,
                    severity=Severity.INFO,
                    category="unused-import",
                    message=f"«{name}» import شده اما استفاده نشده است.",
                    file=filename,
                    line=node.lineno,
                    column=node.col_offset + 1,
                    confidence=0.9,
                    source="ast",
                    suggestion=f"اگر لازم نیست، خط import مربوط به «{name}» را حذف کنید.",
                )
            )

        return diagnostics
