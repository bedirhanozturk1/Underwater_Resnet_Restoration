from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


@dataclass(frozen=True)
class PairReport:
    clear_count: int
    turbid_count: int
    matched_count: int
    missing_clear: tuple[str, ...]
    missing_turbid: tuple[str, ...]


def list_images(root: Path) -> dict[str, Path]:
    """Return image files keyed by filename."""
    if not root.exists():
        raise FileNotFoundError(f"Image directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Expected directory, got: {root}")

    images: dict[str, Path] = {}
    duplicates: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        key = path.name
        if key in images:
            duplicates.append(key)
            continue
        images[key] = path

    if duplicates:
        duplicate_text = ", ".join(sorted(set(duplicates))[:10])
        raise ValueError(f"Duplicate image filenames found under {root}: {duplicate_text}")
    return images


def collect_pairs(clear_dir: Path, turbid_dir: Path) -> tuple[list[tuple[str, Path, Path]], PairReport]:
    clear_images = list_images(clear_dir)
    turbid_images = list_images(turbid_dir)

    clear_names = set(clear_images)
    turbid_names = set(turbid_images)
    matched_names = sorted(clear_names & turbid_names, key=_natural_key)
    missing_clear = tuple(sorted(turbid_names - clear_names, key=_natural_key))
    missing_turbid = tuple(sorted(clear_names - turbid_names, key=_natural_key))

    pairs = [(name, clear_images[name], turbid_images[name]) for name in matched_names]
    report = PairReport(
        clear_count=len(clear_images),
        turbid_count=len(turbid_images),
        matched_count=len(pairs),
        missing_clear=missing_clear,
        missing_turbid=missing_turbid,
    )
    return pairs, report


def split_pairs(
    filenames: Iterable[str],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, list[str]]:
    filenames = list(filenames)
    if not filenames:
        raise ValueError("No filenames were provided for splitting")
    if train_ratio <= 0 or val_ratio < 0 or train_ratio + val_ratio >= 1:
        raise ValueError("Expected train_ratio > 0, val_ratio >= 0, and train_ratio + val_ratio < 1")

    rng = random.Random(seed)
    shuffled = filenames[:]
    rng.shuffle(shuffled)

    train_end = int(len(shuffled) * train_ratio)
    val_end = train_end + int(len(shuffled) * val_ratio)
    return {
        "train": sorted(shuffled[:train_end], key=_natural_key),
        "val": sorted(shuffled[train_end:val_end], key=_natural_key),
        "test": sorted(shuffled[val_end:], key=_natural_key),
    }


def write_splits(splits: dict[str, list[str]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for split_name, filenames in splits.items():
        (output_dir / f"{split_name}.txt").write_text("\n".join(filenames) + "\n", encoding="utf-8")


def write_report(report: PairReport, splits: dict[str, list[str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Checkpoint 1 Dataset Report",
        "===========================",
        "",
        f"Clear images: {report.clear_count}",
        f"Turbid images: {report.turbid_count}",
        f"Matched pairs: {report.matched_count}",
        f"Missing clear images: {len(report.missing_clear)}",
        f"Missing turbid images: {len(report.missing_turbid)}",
        "",
        "Splits",
        "------",
        f"Train: {len(splits['train'])}",
        f"Validation: {len(splits['val'])}",
        f"Test: {len(splits['test'])}",
    ]
    if report.missing_clear:
        lines.extend(["", "First missing clear filenames:", *report.missing_clear[:10]])
    if report.missing_turbid:
        lines.extend(["", "First missing turbid filenames:", *report.missing_turbid[:10]])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_pair_grid(
    pairs: list[tuple[str, Path, Path]],
    output_path: Path,
    max_pairs: int = 6,
    image_size: int = 160,
) -> None:
    if not pairs:
        raise ValueError("No pairs available for visualization")

    selected = pairs[:max_pairs]
    label_height = 34
    cols = 2
    rows = len(selected)
    canvas = Image.new("RGB", (cols * image_size, rows * (image_size + label_height)), "white")
    draw = ImageDraw.Draw(canvas)

    for row, (filename, clear_path, turbid_path) in enumerate(selected):
        y = row * (image_size + label_height)
        turbid = _load_square(turbid_path, image_size)
        clear = _load_square(clear_path, image_size)
        canvas.paste(turbid, (0, y + label_height))
        canvas.paste(clear, (image_size, y + label_height))
        draw.text((5, y + 4), f"Turbid: {filename}", fill="black", font=ImageFont.load_default())
        draw.text((image_size + 5, y + 4), f"Clear: {filename}", fill="black", font=ImageFont.load_default())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)


def _load_square(path: Path, size: int) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB").resize((size, size), Image.Resampling.BILINEAR)


def _natural_key(value: str) -> tuple[int, str] | tuple[int, int, str]:
    stem = Path(value).stem
    if stem.isdigit():
        return (0, int(stem), value)
    return (1, value)
