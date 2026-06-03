from __future__ import annotations

from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


class UnderwaterPairedDataset(Dataset):
    def __init__(
        self,
        clear_dir: Path | str,
        turbid_dir: Path | str,
        split_file: Path | str,
        image_size: int = 128,
        augment: bool = False,
    ) -> None:
        self.clear_dir = Path(clear_dir)
        self.turbid_dir = Path(turbid_dir)
        self.split_file = Path(split_file)
        self.image_size = image_size
        self.augment = augment

        if not self.split_file.exists():
            raise FileNotFoundError(f"Split file does not exist: {self.split_file}")

        self.filenames = [line.strip() for line in self.split_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not self.filenames:
            raise ValueError(f"Split file is empty: {self.split_file}")

        self.resize = transforms.Resize((image_size, image_size), antialias=True)
        self.to_tensor = transforms.ToTensor()
        self.normalize = transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))

    def __len__(self) -> int:
        return len(self.filenames)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor | str]:
        filename = self.filenames[index]
        clear = self._load_image(self.clear_dir / filename)
        turbid = self._load_image(self.turbid_dir / filename)

        if self.augment and torch.rand(()) < 0.5:
            clear = transforms.functional.hflip(clear)
            turbid = transforms.functional.hflip(turbid)

        return {
            "clear": self._to_normalized_tensor(clear),
            "turbid": self._to_normalized_tensor(turbid),
            "filename": filename,
        }

    def _load_image(self, path: Path) -> Image.Image:
        if not path.exists():
            raise FileNotFoundError(f"Missing paired image: {path}")
        with Image.open(path) as image:
            return image.convert("RGB")

    def _to_normalized_tensor(self, image: Image.Image) -> torch.Tensor:
        tensor = self.to_tensor(self.resize(image))
        return self.normalize(tensor)


def denormalize_image(tensor: torch.Tensor) -> torch.Tensor:
    return ((tensor * 0.5) + 0.5).clamp(0.0, 1.0)
