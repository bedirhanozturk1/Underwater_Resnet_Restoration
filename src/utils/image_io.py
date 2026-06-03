from __future__ import annotations

from pathlib import Path

import torch
from PIL import Image, ImageDraw, ImageFont


def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    tensor = tensor.detach().cpu().clamp(0.0, 1.0)
    array = (tensor.permute(1, 2, 0).numpy() * 255.0).round().astype("uint8")
    return Image.fromarray(array)


def save_labeled_grid(images: list[tuple[str, Image.Image]], output_path: Path, columns: int) -> None:
    if not images:
        raise ValueError("No images were provided for grid saving")
    if columns <= 0:
        raise ValueError("columns must be positive")

    width, height = images[0][1].size
    label_height = 24
    rows = (len(images) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * width, rows * (height + label_height)), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    for idx, (label, image) in enumerate(images):
        row = idx // columns
        col = idx % columns
        x = col * width
        y = row * (height + label_height)
        canvas.paste(image.convert("RGB"), (x, y + label_height))
        draw.text((x + 4, y + 4), label, fill="black", font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
