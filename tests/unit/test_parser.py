import ast

from codemind.parser import Parser


def test_parses_valid_source() -> None:
    result = Parser().parse_source("answer = 42\n")

    assert isinstance(result.tree, ast.Module)
    assert result.source == "answer = 42\n"
    assert result.diagnostics == ()


def test_reports_syntax_error_with_location() -> None:
    result = Parser().parse_source("if True print('hi')\n", "example.py")

    assert result.tree is None
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.rule_id == "CM000"
    assert diagnostic.category == "syntax"
    assert diagnostic.file == "example.py"
    assert diagnostic.line == 1
    assert diagnostic.column >= 1


def test_preserves_filename_for_valid_source() -> None:
    result = Parser().parse_source("print(1)\n", "project/main.py")

    assert result.filename == "project/main.py"
    assert result.diagnostics == ()


def test_reads_file_using_python_encoding_declaration(tmp_path) -> None:
    path = tmp_path / "example.py"
    path.write_bytes(b"# coding: latin-1\nname = 'caf\xe9'\n")

    result = Parser().parse_file(path)

    assert isinstance(result.tree, ast.Module)
    assert "café" in result.source
    assert result.diagnostics == ()


def test_reports_missing_file_without_crashing(tmp_path) -> None:
    result = Parser().parse_file(tmp_path / "missing.py")

    assert result.tree is None
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].rule_id == "CM003"


def test_reports_syntax_error_in_file(tmp_path) -> None:
    path = tmp_path / "broken.py"
    path.write_text("if True print('hi')\n", encoding="utf-8")

    result = Parser().parse_file(path)

    assert result.tree is None
    assert result.diagnostics[0].rule_id == "CM000"
    assert result.diagnostics[0].file == str(path)


def test_parses_empty_source() -> None:
    result = Parser().parse_source("")
    assert isinstance(result.tree, ast.Module)
    assert len(result.tree.body) == 0


def test_handles_unicode_characters() -> None:
    source = "name = 'طاها'\n"
    result = Parser().parse_source(source)
    assert result.tree is not None
    assert result.diagnostics == ()


def test_reports_indentation_error() -> None:
    result = Parser().parse_source("def func():\nprint('bad indent')")
    assert result.tree is None
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].rule_id == "CM000"


def test_parses_docstrings_correctly() -> None:
    source = '"""Docstring."""\nx = 1\n'
    result = Parser().parse_source(source)
    assert result.tree is not None
    assert ast.get_docstring(result.tree) == "Docstring."
