from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.dataset import UnderwaterPairedDataset, denormalize_image
from src.models.diffusion import DiffusionSchedule
from src.utils.image_io import save_labeled_grid, tensor_to_pil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize paired batches and forward diffusion noising.")
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
        "--split-file",
        type=Path,
        default=Path("data/splits/train.txt"),
        help="Split file containing paired filenames.",
    )
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=Path("results/checkpoint2"),
        help="Directory where visualization files will be written.",
    )
    parser.add_argument("--image-size", type=int, default=128, help="Image size for visualization.")
    parser.add_argument("--timesteps", type=int, default=300, help="Number of diffusion timesteps.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = UnderwaterPairedDataset(
        clear_dir=args.clear_dir,
        turbid_dir=args.turbid_dir,
        split_file=args.split_file,
        image_size=args.image_size,
        augment=False,
    )
    loader = DataLoader(dataset, batch_size=4, shuffle=False, num_workers=0)
    batch = next(iter(loader))

    sample_images = []
    for idx in range(min(4, batch["clear"].shape[0])):
        filename = batch["filename"][idx]
        sample_images.append((f"turbid {filename}", tensor_to_pil(denormalize_image(batch["turbid"][idx]))))
        sample_images.append((f"clear {filename}", tensor_to_pil(denormalize_image(batch["clear"][idx]))))
    save_labeled_grid(sample_images, args.result_dir / "sample_batch.png", columns=2)

    schedule = DiffusionSchedule(args.timesteps)
    clear = batch["clear"][:1]
    fixed_noise = torch.randn_like(clear)
    selected_timesteps = [0, args.timesteps // 4, args.timesteps // 2, (3 * args.timesteps) // 4, args.timesteps - 1]

    diffusion_images = [("clear t=0", tensor_to_pil(denormalize_image(clear[0])))]
    for timestep in selected_timesteps[1:]:
        t = torch.tensor([timestep], dtype=torch.long)
        noised, _ = schedule.q_sample(clear, t, noise=fixed_noise)
        diffusion_images.append((f"t={timestep}", tensor_to_pil(denormalize_image(noised[0]))))
    save_labeled_grid(diffusion_images, args.result_dir / "forward_diffusion_grid.png", columns=len(diffusion_images))

    print(f"Dataset size: {len(dataset)}")
    print(f"Batch turbid shape: {tuple(batch['turbid'].shape)}")
    print(f"Batch clear shape: {tuple(batch['clear'].shape)}")
    print(f"Tensor min/max: {batch['clear'].min().item():.4f}, {batch['clear'].max().item():.4f}")
    print(f"Sample batch written to: {args.result_dir / 'sample_batch.png'}")
    print(f"Forward diffusion grid written to: {args.result_dir / 'forward_diffusion_grid.png'}")


if __name__ == "__main__":
    main()
