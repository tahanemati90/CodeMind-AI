import pathlib

from codemind.benchmarks.benchmark_runner import BenchmarkRunner

dataset = [
    {"actual": True, "expected": True},
    {"actual": True, "expected": True},
    {"actual": False, "expected": False},
    {"actual": True, "expected": False},  # False Positive
    {"actual": False, "expected": True},  # False Negative
    {"actual": True, "expected": True},
]

runner = BenchmarkRunner()
result = runner.evaluate(dataset)

pathlib.Path("benchmark_report.md").write_text(result.to_markdown(), encoding="utf-8")
pathlib.Path("benchmark_report.json").write_text(result.to_json(), encoding="utf-8")

print("Benchmark reports generated successfully!")
