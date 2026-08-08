from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.prepare_pairs import (
    collect_pairs,
    remove_exact_pair_duplicates,
    split_contiguous_source_groups,
    write_splits,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create source-grouped underwater patch splits with exact-pair deduplication.")
    parser.add_argument("--clear-dir", type=Path, required=True)
    parser.add_argument("--turbid-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--group-size", type=int, default=24)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--split-id", default="grouped_v1_contiguous_24")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pairs, report = collect_pairs(args.clear_dir, args.turbid_dir)
    if report.missing_clear or report.missing_turbid:
        raise ValueError("Grouped splitting requires complete filename pairing")

    pair_paths = {filename: (clear_path, turbid_path) for filename, clear_path, turbid_path in pairs}
    raw_splits, source_groups = split_contiguous_source_groups(
        pair_paths,
        group_size=args.group_size,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
    )
    splits, removed = remove_exact_pair_duplicates(raw_splits, pair_paths)
    _validate_group_isolation(raw_splits, source_groups)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_splits(splits, args.output_dir)
    _write_filename_manifest(args.output_dir / "filename_group.csv", raw_splits, source_groups, removed)

    split_groups = {
        name: sorted({source_groups[filename] for filename in filenames})
        for name, filenames in raw_splits.items()
    }
    manifest = {
        "split_id": args.split_id,
        "group_rule": f"numeric filename stem // {args.group_size}",
        "assignment": "contiguous source groups in numeric filename order",
        "deduplication": "exact clear+turbid byte duplicates; retain one copy with test > val > train priority",
        "matched_pairs_before_deduplication": len(pairs),
        "source_group_count": len(set(source_groups.values())),
        "group_size": args.group_size,
        "split_group_counts": {name: len(groups) for name, groups in split_groups.items()},
        "split_group_ranges": {
            name: [min(groups), max(groups)] if groups else [] for name, groups in split_groups.items()
        },
        "split_image_counts_before_deduplication": {name: len(values) for name, values in raw_splits.items()},
        "split_image_counts_after_deduplication": {name: len(values) for name, values in splits.items()},
        "removed_exact_duplicate_count": len(removed),
        "removed_exact_duplicates": removed,
        "limitations": [
            "The 24-patch source grouping is inferred from the repeated chart structure and numeric filenames; no acquisition manifest was available.",
            "Source grouping and exact deduplication do not guarantee independence between nearby observations from the same physical acquisition session.",
            "Clear targets repeat across source groups because the task uses 24 canonical chart-patch references.",
        ],
    }
    (args.output_dir / "split_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def _validate_group_isolation(splits: dict[str, list[str]], source_groups: dict[str, int]) -> None:
    groups_by_split = {
        name: {source_groups[filename] for filename in filenames}
        for name, filenames in splits.items()
    }
    names = list(groups_by_split)
    for index, first in enumerate(names):
        for second in names[index + 1:]:
            overlap = groups_by_split[first] & groups_by_split[second]
            if overlap:
                raise ValueError(f"Source groups overlap between {first} and {second}: {sorted(overlap)}")


def _write_filename_manifest(
    output_path: Path,
    raw_splits: dict[str, list[str]],
    source_groups: dict[str, int],
    removed: dict[str, str],
) -> None:
    rows = []
    for split_name, filenames in raw_splits.items():
        for filename in filenames:
            rows.append({
                "filename": filename,
                "source_group": source_groups[filename],
                "split": split_name,
                "included": "no" if filename in removed else "yes",
                "exclusion_reason": removed.get(filename, ""),
            })
    rows.sort(key=lambda row: int(Path(str(row["filename"])).stem))
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
