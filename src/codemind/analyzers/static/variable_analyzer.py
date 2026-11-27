"""تحلیل نام‌ها با پشتهٔ اسکوپ و احترام به ترتیب اجرا."""

import ast
import builtins

from codemind.diagnostics import Diagnostic, Severity

_BUILTIN_NAMES = frozenset(dir(builtins))


class _Scope:
    """یک محدودهٔ نام‌گذاری (ماژول، تابع، کلاس یا comprehension)."""

    __slots__ = ("kind", "defined", "globals", "nonlocals")

    def __init__(self, kind: str) -> None:
        self.kind = kind
        self.defined: set[str] = set()
        self.globals: set[str] = set()
        self.nonlocals: set[str] = set()


class _ScopeVisitor(ast.NodeVisitor):
    """پیمایش AST با نگه‌داشتن پشتهٔ اسکوپ‌ها."""

    def __init__(self) -> None:
        self.stack: list[_Scope] = [_Scope("module")]
        self.undefined: list[ast.Name] = []

    # ---------- کمکی‌ها ----------

    def _current(self) -> _Scope:
        return self.stack[-1]

    def _lookup(self, name: str) -> bool:
        """آیا نام در اسکوپ جاری یا والدها (با رعایت global/nonlocal) تعریف شده؟"""
        current = self._current()
        if name in current.globals:
            return name in self.stack[0].defined
        if name in current.nonlocals:
            return any(name in scope.defined for scope in self.stack[1:-1])

        for scope in reversed(self.stack):
            if name in scope.defined:
                return True
        return False

    def _bind(self, name: str) -> None:
        current = self._current()
        if name in current.globals:
            self.stack[0].defined.add(name)
        else:
            current.defined.add(name)

    def _push(self, kind: str) -> None:
        self.stack.append(_Scope(kind))

    def _pop(self) -> None:
        self.stack.pop()

    # ---------- بازدیدها ----------

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self._bind(node.id)
        elif isinstance(node.ctx, ast.Load):
            if node.id not in _BUILTIN_NAMES and not self._lookup(node.id):
                self.undefined.append(node)

    def visit_Global(self, node: ast.Global) -> None:
        self._current().globals.update(node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self._current().nonlocals.update(node.names)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # نام تابع در اسکوپ بیرونی تعریف می‌شود
        self._bind(node.name)

        # decorators و مقادیر پیش‌فرض در اسکوپ بیرونی ارزیابی می‌شوند
        for decorator in node.decorator_list:
            self.visit(decorator)
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self.visit(default)

        self._push("function")
        args = node.args
        for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs):
            self._bind(arg.arg)
        if args.vararg:
            self._bind(args.vararg.arg)
        if args.kwarg:
            self._bind(args.kwarg.arg)

        for statement in node.body:
            self.visit(statement)
        self._pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._push("function")
        args = node.args
        for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs):
            self._bind(arg.arg)
        if args.vararg:
            self._bind(args.vararg.arg)
        if args.kwarg:
            self._bind(args.kwarg.arg)
        self.visit(node.body)
        self._pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._bind(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)

        self._push("class")
        for statement in node.body:
            self.visit(statement)
        self._pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._bind(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name != "*":
                self._bind(alias.asname or alias.name)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is not None:
            self.visit(node.type)
        if node.name:
            self._bind(node.name)
        for statement in node.body:
            self.visit(statement)

    def _visit_comprehension(self, node: ast.AST, elts: list[ast.expr]) -> None:
        generators = node.generators  # type: ignore[attr-defined]
        self.visit(generators[0].iter)
        self._push("comprehension")
        for index, generator in enumerate(generators):
            if index > 0:
                self.visit(generator.iter)
            self.visit(generator.target)
            for condition in generator.ifs:
                self.visit(condition)
        for elt in elts:
            self.visit(elt)
        self._pop()

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._visit_comprehension(node, [node.elt])

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._visit_comprehension(node, [node.elt])

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._visit_comprehension(node, [node.elt])

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._visit_comprehension(node, [node.key, node.value])


class UndefinedVariableAnalyzer:
    """پیدا کردن نام‌هایی که قبل از تعریف یا بیرون از دسترس استفاده شده‌اند."""

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
        reported: set[tuple[str, int]] = set()

        for name_node in visitor.undefined:
            key = (name_node.id, name_node.lineno)
            if key in reported:
                continue
            reported.add(key)

            name = name_node.id
            message = f"نام «{name}» استفاده شده اما در این نقطه تعریف نشده است."
            suggestion = (
                f"«{name}» را قبل از استفاده تعریف کنید یا اگر نام متغیر اشتباه است "
                "املای آن را بررسی کنید."
            )
            diagnostics.append(
                Diagnostic(
                    rule_id=self.rule_id,
                    severity=Severity.WARNING,
                    category="undefined-name",
                    message=message,
                    file=filename,
                    line=name_node.lineno,
                    column=name_node.col_offset + 1,
                    confidence=0.85,
                    source="ast",
                    suggestion=suggestion,
                )
            )

        return diagnostics
