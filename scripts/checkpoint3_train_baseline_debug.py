from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from torch.utils.data import DataLoader, Subset

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.dataset import UnderwaterPairedDataset, denormalize_image
from src.models.diffusion import DiffusionSchedule
from src.models.unet import ConditionalUNet
from src.training.train import diffusion_training_step
from src.utils.image_io import save_labeled_grid, tensor_to_pil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a tiny baseline U-Net diffusion debug training job.")
    parser.add_argument("--clear-dir", type=Path, default=Path("data/datasets/clear_underwater_color_patch/canon_patch"))
    parser.add_argument("--turbid-dir", type=Path, default=Path("data/datasets/turbidty_underwater_color_patch"))
    parser.add_argument("--split-file", type=Path, default=Path("data/splits/train.txt"))
    parser.add_argument("--result-dir", type=Path, default=Path("results/checkpoint3"))
    parser.add_argument("--log-dir", type=Path, default=Path("logs/checkpoint3"))
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("checkpoints/checkpoint3"))
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--subset-size", type=int, default=16)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--timesteps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset = UnderwaterPairedDataset(args.clear_dir, args.turbid_dir, args.split_file, image_size=args.image_size)
    subset = Subset(dataset, list(range(min(args.subset_size, len(dataset)))))
    loader = DataLoader(subset, batch_size=args.batch_size, shuffle=True, num_workers=0)

    model = ConditionalUNet(base_channels=16, time_dim=64).to(device)
    schedule = DiffusionSchedule(args.timesteps, device=device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.result_dir.mkdir(parents=True, exist_ok=True)
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.log_dir / "baseline_debug_training.csv"

    losses: list[float] = []
    with log_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["step", "loss"])
        writer.writeheader()
        iterator = iter(loader)
        for step in range(1, args.steps + 1):
            try:
                batch = next(iterator)
            except StopIteration:
                iterator = iter(loader)
                batch = next(iterator)
            loss = diffusion_training_step(model, batch, schedule, optimizer, device=device)
            losses.append(loss)
            writer.writerow({"step": step, "loss": f"{loss:.6f}"})
            print(f"step {step}/{args.steps} loss={loss:.6f}")

    torch.save({"model_state_dict": model.state_dict(), "steps": args.steps}, args.checkpoint_dir / "baseline_debug.pth")
    _save_loss_curve(losses, args.result_dir / "baseline_loss_curve.png")
    _save_early_restoration_grid(model, schedule, dataset[0], args.result_dir / "baseline_early_restoration.png", device)

    print(f"Log written to: {log_path}")
    print(f"Checkpoint written to: {args.checkpoint_dir / 'baseline_debug.pth'}")
    print(f"Loss curve written to: {args.result_dir / 'baseline_loss_curve.png'}")
    print(f"Early output grid written to: {args.result_dir / 'baseline_early_restoration.png'}")


def _save_loss_curve(losses: list[float], output_path: Path) -> None:
    plt.figure(figsize=(6, 4))
    plt.plot(range(1, len(losses) + 1), losses, marker="o")
    plt.xlabel("Step")
    plt.ylabel("Noise prediction loss")
    plt.title("Baseline Debug Training Loss")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


@torch.no_grad()
def _save_early_restoration_grid(
    model: ConditionalUNet,
    schedule: DiffusionSchedule,
    sample: dict[str, torch.Tensor | str],
    output_path: Path,
    device: torch.device,
) -> None:
    model.eval()
    clear = sample["clear"].unsqueeze(0).to(device)  # type: ignore[union-attr]
    turbid = sample["turbid"].unsqueeze(0).to(device)  # type: ignore[union-attr]
    timestep = torch.tensor([schedule.timesteps - 1], dtype=torch.long, device=device)
    noisy, _ = schedule.q_sample(clear, timestep)
    predicted_noise = model(noisy, turbid, timestep)
    alpha = schedule.sqrt_alpha_cumprod[timestep].reshape(1, 1, 1, 1)
    sigma = schedule.sqrt_one_minus_alpha_cumprod[timestep].reshape(1, 1, 1, 1)
    early_estimate = (noisy - sigma * predicted_noise) / alpha.clamp_min(1e-8)

    images = [
        ("turbid input", tensor_to_pil(denormalize_image(turbid[0].cpu()))),
        ("early estimate", tensor_to_pil(denormalize_image(early_estimate[0].cpu()))),
        ("clear target", tensor_to_pil(denormalize_image(clear[0].cpu()))),
    ]
    save_labeled_grid(images, output_path, columns=3)


if __name__ == "__main__":
    main()
