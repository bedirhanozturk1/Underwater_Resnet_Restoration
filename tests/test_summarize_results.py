import pytest

from scripts.summarize_results import METRICS, _aggregate_seed_rows


def _row(model: str, seed: int, value: float, n: int = 384) -> dict[str, str]:
    row = {"experiment": f"{model}:{seed}", "model": model, "seed": str(seed), "n": str(n)}
    row.update({metric: str(value) for metric in METRICS})
    return row


def test_seed_aggregation_reports_sample_standard_deviation() -> None:
    result = _aggregate_seed_rows([
        _row("baseline", 42, 1.0),
        _row("baseline", 123, 2.0),
        _row("baseline", 2026, 3.0),
    ])

    assert result[0]["runs"] == "3"
    assert result[0]["n_per_run"] == "384"
    assert result[0]["mse_mean"] == "2.000000"
    assert result[0]["mse_std"] == "1.000000"


def test_seed_aggregation_rejects_different_test_counts() -> None:
    with pytest.raises(ValueError, match="row counts differ"):
        _aggregate_seed_rows([_row("baseline", 42, 1.0), _row("baseline", 123, 2.0, n=383)])
