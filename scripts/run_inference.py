from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.dataset import denormalize_image
from src.models.diffusion import DiffusionSchedule
from src.models.factory import build_model
from src.models.sampling import sample_conditioned_image
from src.utils.image_io import tensor_to_pil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore images from a trained conditional diffusion checkpoint.")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/results/inference"))
    parser.add_argument("--limit", type=int, default=0, help="Optional image limit for quick demos; 0 means all images.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(args.checkpoint, map_location=device)
    image_size = int(checkpoint["image_size"])
    model = build_model(checkpoint["model"], checkpoint["base_channels"], checkpoint["time_dim"]).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    schedule = DiffusionSchedule(int(checkpoint["timesteps"]), device=device)

    transform = transforms.Compose([
        transforms.Resize((image_size, image_size), antialias=True),
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
    ])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = [path for path in sorted(args.input_dir.rglob("*")) if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}]
    if args.limit > 0:
        image_paths = image_paths[: args.limit]
    for path in image_paths:
        with Image.open(path) as image:
            condition = transform(image.convert("RGB")).unsqueeze(0).to(device)
        restored = sample_conditioned_image(model, condition, schedule, device)[0].cpu()
        output = tensor_to_pil(denormalize_image(restored))
        output.save(args.output_dir / f"{path.stem}_restored.png")
    print(f"Restored {len(image_paths)} images to {args.output_dir}")


if __name__ == "__main__":
    main()
