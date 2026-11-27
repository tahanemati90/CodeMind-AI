from codemind.runtime.debug_engine import DebugEngine


def test_debug_engine_success() -> None:
    engine = DebugEngine()
    result = engine.execute('print("Hello from CodeMind")')
    assert result.exit_code == 0
    assert "Hello from CodeMind" in result.stdout
    assert not result.timed_out


def test_debug_engine_runtime_error() -> None:
    engine = DebugEngine()
    result = engine.execute("print(1 / 0)")
    assert result.exit_code != 0
    assert "ZeroDivisionError" in result.stderr
    assert result.traceback is not None


def test_debug_engine_timeout() -> None:
    engine = DebugEngine(timeout_seconds=1.0)
    result = engine.execute("while True: pass")
    assert result.timed_out
    assert result.exit_code == -1
