import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    total_samples: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    def to_markdown(self) -> str:
        return f"""# CodeMind AI Benchmark Report
- Total Samples: {self.total_samples}
- True Positives: {self.true_positives}
- False Positives: {self.false_positives}
- False Negatives: {self.false_negatives}
- Precision: {self.precision:.2f}
- Recall: {self.recall:.2f}
- F1 Score: {self.f1_score:.2f}
"""


class BenchmarkRunner:
    def evaluate(self, dataset: list[dict]) -> BenchmarkResult:
        tp = sum(1 for item in dataset if item.get("actual") and item.get("expected"))
        fp = sum(1 for item in dataset if item.get("actual") and not item.get("expected"))
        fn = sum(1 for item in dataset if not item.get("actual") and item.get("expected"))

        total = len(dataset)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return BenchmarkResult(
            total_samples=total,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            precision=precision,
            recall=recall,
            f1_score=f1,
        )
