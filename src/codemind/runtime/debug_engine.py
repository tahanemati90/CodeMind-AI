import subprocess
import sys
import tempfile
from pathlib import Path

from codemind.diagnostics.models import ExecutionResult


class DebugEngine:
    """موتور اجرای ایزوله برای کدهای پایتون با قابلیت کنترل Timeout و جمع‌آوری خروجی‌ها."""

    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self.timeout_seconds = timeout_seconds

    def execute(self, source_code: str) -> ExecutionResult:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file.write(source_code)
            temp_file_path = temp_file.name

        try:
            process = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            return ExecutionResult(
                stdout=process.stdout,
                stderr=process.stderr,
                exit_code=process.returncode,
                timed_out=False,
                traceback=process.stderr if process.returncode != 0 else None,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                stdout="",
                stderr="Execution exceeded the time limit.",
                exit_code=-1,
                timed_out=True,
                traceback="TimeoutExpired",
            )
        finally:
            Path(temp_file_path).unlink(missing_ok=True)
