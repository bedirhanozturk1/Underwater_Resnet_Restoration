from pathlib import Path

import torch
from PIL import Image

from src.data.dataset import UnderwaterPairedDataset


def test_underwater_paired_dataset_returns_expected_keys_and_shapes(tmp_path: Path) -> None:
    clear_dir = tmp_path / "clear"
    turbid_dir = tmp_path / "turbid"
    clear_dir.mkdir()
    turbid_dir.mkdir()

    _save_image(clear_dir / "1.jpg", (255, 255, 255))
    _save_image(turbid_dir / "1.jpg", (0, 64, 128))
    split_file = tmp_path / "train.txt"
    split_file.write_text("1.jpg\n", encoding="utf-8")

    dataset = UnderwaterPairedDataset(clear_dir, turbid_dir, split_file, image_size=32)
    sample = dataset[0]

    assert set(sample) == {"clear", "turbid", "filename"}
    assert sample["filename"] == "1.jpg"
    assert isinstance(sample["clear"], torch.Tensor)
    assert isinstance(sample["turbid"], torch.Tensor)
    assert sample["clear"].shape == (3, 32, 32)
    assert sample["turbid"].shape == (3, 32, 32)
    assert sample["clear"].min() >= -1.0
    assert sample["clear"].max() <= 1.0
    assert sample["turbid"].min() >= -1.0
    assert sample["turbid"].max() <= 1.0


def _save_image(path: Path, color: tuple[int, int, int]) -> None:
    Image.new("RGB", (16, 16), color).save(path)
