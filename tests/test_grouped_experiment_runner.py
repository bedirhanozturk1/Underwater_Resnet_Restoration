import json

from scripts.run_grouped_experiments import _evaluation_complete, _is_complete


def test_completion_marker_must_match_full_run(tmp_path) -> None:
    marker = tmp_path / "completed.json"
    marker.write_text(json.dumps({
        "run_name": "baseline_b32",
        "model": "baseline",
        "seed": 42,
        "split_id": "grouped_v1_contiguous_24",
        "epochs": 50,
    }), encoding="utf-8")

    assert _is_complete(marker, "baseline_b32", "baseline", 42, 50)
    assert not _is_complete(marker, "baseline_b32", "baseline", 42, 100)
    assert not _is_complete(marker, "baseline_b32", "baseline", 123, 50)


def test_evaluation_marker_requires_expected_test_count(tmp_path) -> None:
    marker = tmp_path / "evaluation_manifest.json"
    manifest = {
        "run_name": "baseline_b32_seed_42",
        "training_seed": 42,
        "evaluation_seed": 2026,
        "split_id": "grouped_v1_contiguous_24",
        "n": 384,
    }
    marker.write_text(json.dumps(manifest), encoding="utf-8")

    assert _evaluation_complete(marker, "baseline_b32_seed_42", 42, 2026)
    manifest["n"] = 383
    marker.write_text(json.dumps(manifest), encoding="utf-8")
    assert not _evaluation_complete(marker, "baseline_b32_seed_42", 42, 2026)
