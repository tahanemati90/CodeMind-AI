"""Parse Python source without executing it."""

import ast
import tokenize
from dataclasses import dataclass
from pathlib import Path

from codemind.diagnostics.models import Diagnostic, Severity


@dataclass(frozen=True, slots=True)
class ParsedSource:
    source: str
    filename: str
    tree: ast.Module | None
    diagnostics: tuple[Diagnostic, ...]


class Parser:
    """Read and parse source code and report syntax or file errors."""

    def parse_source(self, source: str, filename: str = "<memory>") -> ParsedSource:
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as error:
            diagnostic = Diagnostic(
                rule_id="CM000",
                severity=Severity.ERROR,
                category="syntax",
                message=error.msg,
                file=filename,
                line=error.lineno or 1,
                column=error.offset or 1,
                confidence=1.0,
                source="parser",
            )
            return ParsedSource(source, filename, None, (diagnostic,))

        return ParsedSource(source, filename, tree, ())

    def parse_file(self, path: str | Path) -> ParsedSource:
        filename = str(path)
        try:
            with tokenize.open(filename) as stream:
                source = stream.read()
        except (OSError, UnicodeError, SyntaxError) as error:
            diagnostic = Diagnostic(
                rule_id="CM003",
                severity=Severity.ERROR,
                category="source",
                message=f"Cannot read Python source: {error}",
                file=filename,
                line=1,
                column=1,
                confidence=1.0,
                source="parser",
            )
            return ParsedSource("", filename, None, (diagnostic,))

        return self.parse_source(source, filename=filename)
