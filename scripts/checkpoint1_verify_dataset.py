from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.prepare_pairs import collect_pairs, make_pair_grid, split_pairs, write_report, write_splits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify paired underwater restoration dataset.")
    parser.add_argument(
        "--clear-dir",
        type=Path,
        default=Path("data/datasets/clear_underwater_color_patch/canon_patch"),
        help="Directory containing clear/reference images.",
    )
    parser.add_argument(
        "--turbid-dir",
        type=Path,
        default=Path("data/datasets/turbidty_underwater_color_patch"),
        help="Directory containing turbid/degraded images.",
    )
    parser.add_argument(
        "--split-dir",
        type=Path,
        default=Path("data/splits"),
        help="Directory where train/val/test split files will be written.",
    )
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=Path("results/checkpoint1"),
        help="Directory where report and visualization files will be written.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible splits.")
    parser.add_argument("--max-visual-pairs", type=int, default=6, help="Number of pairs in the sample grid.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pairs, report = collect_pairs(args.clear_dir, args.turbid_dir)
    splits = split_pairs([filename for filename, _, _ in pairs], seed=args.seed)

    write_splits(splits, args.split_dir)
    write_report(report, splits, args.result_dir / "dataset_report.txt")
    make_pair_grid(pairs, args.result_dir / "dataset_pair_samples.png", max_pairs=args.max_visual_pairs)

    print(f"Clear images: {report.clear_count}")
    print(f"Turbid images: {report.turbid_count}")
    print(f"Matched pairs: {report.matched_count}")
    print(f"Missing clear images: {len(report.missing_clear)}")
    print(f"Missing turbid images: {len(report.missing_turbid)}")
    print(f"Train split: {len(splits['train'])}")
    print(f"Validation split: {len(splits['val'])}")
    print(f"Test split: {len(splits['test'])}")
    print(f"Report written to: {args.result_dir / 'dataset_report.txt'}")
    print(f"Sample grid written to: {args.result_dir / 'dataset_pair_samples.png'}")


if __name__ == "__main__":
    main()
