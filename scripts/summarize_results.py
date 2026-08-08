from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


METRICS = ["mse", "mae", "psnr", "ssim", "delta_e_cie76", "entropy"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize restoration metrics and training logs for the final report.")
    parser.add_argument("--metric-csv", action="append", default=[], help="Metric CSV as label=path. Can be repeated.")
    parser.add_argument("--log-csv", action="append", default=[], help="Training log CSV as label=path. Can be repeated.")
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
    frame = pd.read_csv(path)
    row = {"experiment": label, "n": str(len(frame))}
    for metric in METRICS:
        row[metric] = f"{frame[metric].mean():.6f}"
    return row


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
        frame = pd.read_csv(path)
        plt.plot(frame["epoch"], frame["train_loss"], label=f"{label} train")
        plt.plot(frame["epoch"], frame["val_loss"], linestyle="--", label=f"{label} val")
    plt.xlabel("Epoch")
    plt.ylabel("Noise prediction loss")
    plt.title("Training and validation loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    main()
