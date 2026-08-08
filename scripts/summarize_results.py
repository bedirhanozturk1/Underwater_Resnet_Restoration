from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


METRICS = ["mse", "mae", "psnr", "ssim", "delta_e_cie76", "entropy"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize restoration metrics and training logs for the final report.")
    parser.add_argument("--metric-csv", action="append", default=[], help="Metric CSV as label=path. Can be repeated.")
    parser.add_argument("--log-csv", action="append", default=[], help="Training log CSV as label=path. Can be repeated.")
    parser.add_argument("--aggregate-seeds", action="store_true", help="Parse metric labels as model:seed and report mean/std across seeds.")
    parser.add_argument("--output-dir", type=Path, default=Path("report_outputs"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metric_rows = [_summarize_metric_csv(label, path) for label, path in _parse_labeled_paths(args.metric_csv)]
    if metric_rows:
        summary_path = args.output_dir / "metric_summary.csv"
        with summary_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(metric_rows[0].keys()))
            writer.writeheader()
            writer.writerows(metric_rows)
        _plot_metric_bars(metric_rows, args.output_dir)
        print(f"Wrote metric summary to {summary_path}")
        if args.aggregate_seeds:
            aggregate_rows = _aggregate_seed_rows(metric_rows)
            aggregate_path = args.output_dir / "metric_summary_mean_std.csv"
            with aggregate_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(aggregate_rows[0].keys()))
                writer.writeheader()
                writer.writerows(aggregate_rows)
            print(f"Wrote seed aggregate to {aggregate_path}")

    log_paths = _parse_labeled_paths(args.log_csv)
    if log_paths:
        _plot_training_logs(log_paths, args.output_dir / "training_loss_curves.png")
        print(f"Wrote training loss curves to {args.output_dir / 'training_loss_curves.png'}")


def _parse_labeled_paths(values: list[str]) -> list[tuple[str, Path]]:
    parsed: list[tuple[str, Path]] = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"Expected label=path, got: {value}")
        label, raw_path = value.split("=", 1)
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(path)
        parsed.append((label, path))
    return parsed


def _summarize_metric_csv(label: str, path: Path) -> dict[str, str]:
    rows = _read_csv(path)
    if not rows:
        raise ValueError(f"Metric CSV is empty: {path}")
    model, seed = _split_model_seed(label)
    row = {"experiment": label, "model": model, "seed": seed, "n": str(len(rows))}
    for metric in METRICS:
        row[metric] = f"{statistics.fmean(float(item[metric]) for item in rows):.6f}"
    return row


def _split_model_seed(label: str) -> tuple[str, str]:
    if ":" not in label:
        return label, ""
    model, seed = label.rsplit(":", 1)
    if not seed.isdigit():
        raise ValueError(f"Expected metric label model:seed, got: {label}")
    return model, seed


def _aggregate_seed_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if any(row["seed"] == "" for row in rows):
        raise ValueError("--aggregate-seeds requires every metric label to use model:seed")
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault(row["model"], []).append(row)
    aggregated = []
    for model, group in groups.items():
        n_values = sorted({int(row["n"]) for row in group})
        if len(n_values) != 1:
            raise ValueError(f"Evaluation row counts differ across seeds for {model}: {n_values}")
        row = {"model": model, "runs": str(len(group)), "n_per_run": str(n_values[0])}
        for metric in METRICS:
            values = [float(item[metric]) for item in group]
            row[f"{metric}_mean"] = f"{statistics.fmean(values):.6f}"
            row[f"{metric}_std"] = f"{statistics.stdev(values):.6f}" if len(values) > 1 else "0.000000"
        aggregated.append(row)
    return aggregated


def _plot_metric_bars(rows: list[dict[str, str]], output_dir: Path) -> None:
    labels = [row["experiment"] for row in rows]
    for metric in ("psnr", "ssim", "delta_e_cie76", "mse"):
        values = [float(row[metric]) for row in rows]
        plt.figure(figsize=(max(7, len(labels) * 1.2), 4))
        plt.bar(labels, values)
        plt.ylabel(metric)
        plt.title(f"{metric} comparison")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(output_dir / f"{metric}_comparison.png")
        plt.close()


def _plot_training_logs(log_paths: list[tuple[str, Path]], output_path: Path) -> None:
    plt.figure(figsize=(8, 5))
    for label, path in log_paths:
        rows = _read_csv(path)
        epochs = [int(row["epoch"]) for row in rows]
        plt.plot(epochs, [float(row["train_loss"]) for row in rows], label=f"{label} train")
        plt.plot(epochs, [float(row["val_loss"]) for row in rows], linestyle="--", label=f"{label} val")
    plt.xlabel("Epoch")
    plt.ylabel("Noise prediction loss")
    plt.title("Training and validation loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    main()
