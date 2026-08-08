from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


MODELS = (
    ("baseline_b32", "baseline", 32),
    ("param_matched_unet_b42", "baseline", 42),
    ("residual_b32", "residual", 32),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the grouped-split 3-model x 3-seed Colab experiment matrix.")
    parser.add_argument("--drive-root", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--evaluation-seed", type=int, default=2026)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    clear_dir = args.drive_root / "datasets/clear_underwater_color_patch/canon_patch"
    turbid_dir = args.drive_root / "datasets/turbidty_underwater_color_patch"
    experiment_root = args.drive_root / "experiments/grouped_v1"
    split_dir = experiment_root / "split"
    summaries_dir = experiment_root / "summaries"

    _run([
        sys.executable,
        str(repo_root / "scripts/create_grouped_splits.py"),
        "--clear-dir", str(clear_dir),
        "--turbid-dir", str(turbid_dir),
        "--output-dir", str(split_dir),
    ])

    metric_args: list[str] = []
    log_args: list[str] = []
    for run_name, model, base_channels in MODELS:
        for seed in args.seeds:
            seed_root = experiment_root / "runs" / run_name / f"seed_{seed}"
            checkpoint_root = seed_root / "checkpoints"
            log_root = seed_root / "logs"
            evaluation_root = seed_root / "evaluation"
            checkpoint = checkpoint_root / run_name / "best.pth"
            latest = checkpoint_root / run_name / "latest.pth"
            completion = checkpoint_root / run_name / "completed.json"
            if not _is_complete(completion, run_name, model, seed, args.epochs):
                command = [
                    sys.executable,
                    str(repo_root / "scripts/train_model.py"),
                    "--model", model,
                    "--run-name", run_name,
                    "--split-id", "grouped_v1_contiguous_24",
                    "--base-channels", str(base_channels),
                    "--seed", str(seed),
                    "--epochs", str(args.epochs),
                    "--batch-size", str(args.batch_size),
                    "--num-workers", str(args.num_workers),
                    "--clear-dir", str(clear_dir),
                    "--turbid-dir", str(turbid_dir),
                    "--split-dir", str(split_dir),
                    "--checkpoint-dir", str(checkpoint_root),
                    "--log-dir", str(log_root),
                ]
                if latest.exists():
                    command.extend(["--resume", str(latest)])
                _run(command)
            else:
                print(f"Skipping completed training run: {run_name} seed {seed}", flush=True)

            if not checkpoint.exists():
                raise FileNotFoundError(f"Completed run has no best checkpoint: {checkpoint}")

            evaluation_name = f"{run_name}_seed_{seed}"
            metrics_path = evaluation_root / f"{evaluation_name}_metrics.csv"
            evaluation_manifest = evaluation_root / f"{evaluation_name}_evaluation_manifest.json"
            if not _evaluation_complete(evaluation_manifest, evaluation_name, seed, args.evaluation_seed):
                _run([
                    sys.executable,
                    str(repo_root / "scripts/evaluate_model.py"),
                    "--checkpoint", str(checkpoint),
                    "--run-name", evaluation_name,
                    "--seed", str(args.evaluation_seed),
                    "--clear-dir", str(clear_dir),
                    "--turbid-dir", str(turbid_dir),
                    "--split-file", str(split_dir / "test.txt"),
                    "--result-dir", str(evaluation_root),
                    "--num-workers", str(args.num_workers),
                ])
            else:
                print(f"Skipping completed evaluation: {evaluation_name}", flush=True)

            if not metrics_path.exists():
                raise FileNotFoundError(f"Completed evaluation has no metrics CSV: {metrics_path}")

            metric_args.extend(["--metric-csv", f"{run_name}:{seed}={metrics_path}"])
            log_args.extend(["--log-csv", f"{run_name}:{seed}={log_root / run_name / 'training.csv'}"])

    _run([
        sys.executable,
        str(repo_root / "scripts/summarize_results.py"),
        *metric_args,
        *log_args,
        "--aggregate-seeds",
        "--output-dir", str(summaries_dir),
    ])
    print(f"Grouped experiment matrix complete: {experiment_root}", flush=True)


def _run(command: list[str]) -> None:
    print("\n$ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def _is_complete(path: Path, run_name: str, model: str, seed: int, epochs: int) -> bool:
    if not path.exists():
        return False
    try:
        completion = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        completion.get("run_name") == run_name
        and completion.get("model") == model
        and completion.get("seed") == seed
        and completion.get("split_id") == "grouped_v1_contiguous_24"
        and completion.get("epochs") == epochs
    )


def _evaluation_complete(path: Path, run_name: str, training_seed: int, evaluation_seed: int) -> bool:
    if not path.exists():
        return False
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        manifest.get("run_name") == run_name
        and manifest.get("training_seed") == training_seed
        and manifest.get("evaluation_seed") == evaluation_seed
        and manifest.get("split_id") == "grouped_v1_contiguous_24"
        and manifest.get("n") == 384
    )


if __name__ == "__main__":
    main()
