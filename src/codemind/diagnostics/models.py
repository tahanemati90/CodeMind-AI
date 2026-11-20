from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    rule_id: str
    severity: Severity
    category: str
    message: str
    file: str
    line: int | None
    column: int | None
    confidence: float
    source: str
    suggestion: str | None = None

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("rule_id cannot be empty")

        if not self.message.strip():
            raise ValueError("message cannot be empty")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        if self.line is not None and self.line < 1:
            raise ValueError("line must be greater than or equal to 1")

        if self.column is not None and self.column < 1:
            raise ValueError("column must be greater than or equal to 1")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data
