from codemind.benchmarks.benchmark_runner import BenchmarkRunner


def test_benchmark_metrics() -> None:
    runner = BenchmarkRunner()
    dataset = [
        {"actual": True, "expected": True},
        {"actual": True, "expected": False},
        {"actual": False, "expected": True},
        {"actual": True, "expected": True},
    ]
    result = runner.evaluate(dataset)
    assert result.total_samples == 4
    assert result.true_positives == 2
    assert result.precision > 0
    assert "Benchmark Report" in result.to_markdown()
    assert "total_samples" in result.to_json()
