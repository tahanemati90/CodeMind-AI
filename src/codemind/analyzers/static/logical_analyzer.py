import ast

from codemind.diagnostics.models import Diagnostic, Severity


class LogicalAnalyzer(ast.NodeVisitor):
    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []

    def analyze(self, source: str) -> list[Diagnostic]:
        self.diagnostics = []
        tree = ast.parse(source)
        self.visit(tree)
        return self.diagnostics

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if not node.body:
            return
        last_stmt = node.body[-1]
        if not isinstance(last_stmt, (ast.Return, ast.Raise)):
            self.diagnostics.append(
                Diagnostic(
                    rule_id="CM007",
                    severity=Severity.WARNING,
                    category="Logical",
                    message="Function does not return a value in all code paths.",
                    file="<unknown>",
                    line=node.lineno,
                    column=node.col_offset + 1,
                    confidence=0.7,
                    source="LogicalAnalyzer",
                    suggestion="Add a 'return' statement at the end of the function.",
                )
            )
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if (
            isinstance(node.op, ast.Div)
            and isinstance(node.right, ast.Constant)
            and node.right.value == 0
        ):
            self.diagnostics.append(
                Diagnostic(
                    rule_id="CM002",
                    severity=Severity.ERROR,
                    category="Logical",
                    message="Division by zero detected.",
                    file="<unknown>",
                    line=node.lineno,
                    column=node.col_offset + 1,
                    confidence=1.0,
                    source="LogicalAnalyzer",
                )
            )
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        sequence_length: int | None = None
        if isinstance(node.value, (ast.List, ast.Tuple)):
            sequence_length = len(node.value.elts)
        elif isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            sequence_length = len(node.value.value)

        index_value: int | None = None
        if isinstance(node.slice, ast.Constant):
            value = node.slice.value
            if isinstance(value, int) and not isinstance(value, bool):
                index_value = value
        elif (
            isinstance(node.slice, ast.UnaryOp)
            and isinstance(node.slice.op, (ast.USub, ast.UAdd))
            and isinstance(node.slice.operand, ast.Constant)
            and isinstance(node.slice.operand.value, int)
            and not isinstance(node.slice.operand.value, bool)
        ):
            value = node.slice.operand.value
            index_value = -value if isinstance(node.slice.op, ast.USub) else value

        if (
            sequence_length is not None
            and index_value is not None
            and (index_value < -sequence_length or index_value >= sequence_length)
        ):
            self.diagnostics.append(
                Diagnostic(
                    rule_id="CM006",
                    severity=Severity.WARNING,
                    category="Logical",
                    message=(
                        f"Index {index_value} is out of range for a sequence "
                        f"of length {sequence_length}."
                    ),
                    file="<unknown>",
                    line=node.lineno,
                    column=node.col_offset + 1,
                    confidence=1.0,
                    source="LogicalAnalyzer",
                    suggestion="Use an index within the sequence bounds.",
                )
            )
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        for op in node.ops:
            if isinstance(op, (ast.Eq, ast.NotEq)):
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and comparator.value is None:
                        self.diagnostics.append(
                            Diagnostic(
                                rule_id="CM003",
                                severity=Severity.WARNING,
                                category="Logical",
                                message="Use 'is None' or 'is not None' to compare with None.",
                                file="<unknown>",
                                line=node.lineno,
                                column=node.col_offset + 1,
                                confidence=0.9,
                                source="LogicalAnalyzer",
                            )
                        )
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        is_constant_true = isinstance(node.test, ast.Constant) and node.test.value is True
        has_break = any(
            isinstance(child, ast.Break)
            for statement in node.body
            for child in ast.walk(statement)
            if not any(
                isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
                for parent in ast.walk(statement)
                if parent is child
            )
        )

        if is_constant_true and not has_break:
            self.diagnostics.append(
                Diagnostic(
                    rule_id="CM005",
                    severity=Severity.WARNING,
                    category="Logical",
                    message="Potential infinite loop: 'while True' has no break.",
                    file="<unknown>",
                    line=node.lineno,
                    column=node.col_offset + 1,
                    confidence=0.8,
                    source="LogicalAnalyzer",
                    suggestion="Add a reachable 'break' condition or update the loop condition.",
                )
            )
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        if isinstance(node.test, ast.Constant) and isinstance(node.test.value, bool):
            self.diagnostics.append(
                Diagnostic(
                    rule_id="CM004",
                    severity=Severity.WARNING,
                    category="Logical",
                    message=f"Constant condition '{node.test.value}' detected.",
                    file="<unknown>",
                    line=node.lineno,
                    column=node.col_offset + 1,
                    confidence=1.0,
                    source="LogicalAnalyzer",
                )
            )
        self.generic_visit(node)
