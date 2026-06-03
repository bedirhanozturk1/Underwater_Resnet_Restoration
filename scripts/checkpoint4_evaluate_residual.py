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
from src.evaluation.metrics import delta_e, entropy, mae, mse, psnr, ssim
from src.models.diffusion import DiffusionSchedule
from src.models.residual_unet import ResidualUNet
from src.models.resnet_blocks import count_parameters
from src.models.unet import ConditionalUNet
from src.training.train import diffusion_training_step
from src.utils.image_io import save_labeled_grid, tensor_to_pil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run residual-backbone debug training and compare with baseline shapes/metrics.")
    parser.add_argument("--clear-dir", type=Path, default=Path("data/datasets/clear_underwater_color_patch/canon_patch"))
    parser.add_argument("--turbid-dir", type=Path, default=Path("data/datasets/turbidty_underwater_color_patch"))
    parser.add_argument("--split-file", type=Path, default=Path("data/splits/train.txt"))
    parser.add_argument("--result-dir", type=Path, default=Path("results/checkpoint4"))
    parser.add_argument("--log-dir", type=Path, default=Path("logs/checkpoint4"))
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("checkpoints/checkpoint4"))
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--subset-size", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--timesteps", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset = UnderwaterPairedDataset(args.clear_dir, args.turbid_dir, args.split_file, image_size=args.image_size)
    subset = Subset(dataset, list(range(min(args.subset_size, len(dataset)))))
    loader = DataLoader(subset, batch_size=args.batch_size, shuffle=True, num_workers=0)

    baseline = ConditionalUNet(base_channels=16, time_dim=64).to(device)
    residual = ResidualUNet(base_channels=16, time_dim=64).to(device)
    schedule = DiffusionSchedule(args.timesteps, device=device)
    optimizer = torch.optim.AdamW(residual.parameters(), lr=1e-4)

    args.result_dir.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    losses = _train_debug(residual, schedule, optimizer, loader, args.steps, device, args.log_dir / "residual_debug_training.csv")
    torch.save({"model_state_dict": residual.state_dict(), "steps": args.steps}, args.checkpoint_dir / "residual_debug.pth")

    _write_parameter_comparison(baseline, residual, args.result_dir / "model_parameter_comparison.txt")
    _save_loss_curve(losses, args.result_dir / "training_curves.png")
    _write_metrics_and_grid(baseline, residual, schedule, dataset[0], args.result_dir, device)

    print(f"Baseline parameters: {count_parameters(baseline)}")
    print(f"Residual parameters: {count_parameters(residual)}")
    print(f"Residual debug log written to: {args.log_dir / 'residual_debug_training.csv'}")
    print(f"Residual checkpoint written to: {args.checkpoint_dir / 'residual_debug.pth'}")
    print(f"Checkpoint 4 results written to: {args.result_dir}")


def _train_debug(model, schedule, optimizer, loader, steps: int, device: torch.device, log_path: Path) -> list[float]:
    losses: list[float] = []
    with log_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["step", "loss"])
        writer.writeheader()
        iterator = iter(loader)
        for step in range(1, steps + 1):
            try:
                batch = next(iterator)
            except StopIteration:
                iterator = iter(loader)
                batch = next(iterator)
            loss = diffusion_training_step(model, batch, schedule, optimizer, device=device)
            losses.append(loss)
            writer.writerow({"step": step, "loss": f"{loss:.6f}"})
            print(f"residual step {step}/{steps} loss={loss:.6f}")
    return losses


def _write_parameter_comparison(baseline: ConditionalUNet, residual: ResidualUNet, output_path: Path) -> None:
    output_path.write_text(
        "Model Parameter Comparison\n"
        "==========================\n\n"
        f"Baseline Conditional U-Net parameters: {count_parameters(baseline)}\n"
        f"Residual denoising backbone parameters: {count_parameters(residual)}\n",
        encoding="utf-8",
    )


def _save_loss_curve(losses: list[float], output_path: Path) -> None:
    plt.figure(figsize=(6, 4))
    plt.plot(range(1, len(losses) + 1), losses, marker="o", label="Residual debug")
    plt.xlabel("Step")
    plt.ylabel("Noise prediction loss")
    plt.title("Residual Debug Training Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


@torch.no_grad()
def _write_metrics_and_grid(
    baseline: ConditionalUNet,
    residual: ResidualUNet,
    schedule: DiffusionSchedule,
    sample: dict[str, torch.Tensor | str],
    result_dir: Path,
    device: torch.device,
) -> None:
    baseline.eval()
    residual.eval()
    clear = sample["clear"].unsqueeze(0).to(device)  # type: ignore[union-attr]
    turbid = sample["turbid"].unsqueeze(0).to(device)  # type: ignore[union-attr]
    timestep = torch.tensor([schedule.timesteps - 1], dtype=torch.long, device=device)
    noisy, _ = schedule.q_sample(clear, timestep)
    baseline_estimate = _estimate_clean(baseline, noisy, turbid, timestep, schedule)
    residual_estimate = _estimate_clean(residual, noisy, turbid, timestep, schedule)

    clear_img = denormalize_image(clear[0].cpu())
    turbid_img = denormalize_image(turbid[0].cpu())
    baseline_img = denormalize_image(baseline_estimate[0].cpu())
    residual_img = denormalize_image(residual_estimate[0].cpu())

    rows = [
        _metric_row("Turbid input", turbid_img, clear_img),
        _metric_row("Baseline U-Net debug", baseline_img, clear_img),
        _metric_row("Residual backbone debug", residual_img, clear_img),
    ]
    with (result_dir / "final_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    images = [
        ("turbid input", tensor_to_pil(turbid_img)),
        ("baseline debug", tensor_to_pil(baseline_img)),
        ("residual debug", tensor_to_pil(residual_img)),
        ("clear target", tensor_to_pil(clear_img)),
    ]
    save_labeled_grid(images, result_dir / "final_comparison_grid.png", columns=4)


def _estimate_clean(model, noisy, turbid, timestep, schedule):
    predicted_noise = model(noisy, turbid, timestep)
    alpha = schedule.sqrt_alpha_cumprod[timestep].reshape(1, 1, 1, 1)
    sigma = schedule.sqrt_one_minus_alpha_cumprod[timestep].reshape(1, 1, 1, 1)
    return (noisy - sigma * predicted_noise) / alpha.clamp_min(1e-8)


def _metric_row(name: str, image: torch.Tensor, target: torch.Tensor) -> dict[str, str]:
    return {
        "method": name,
        "mse": f"{mse(image, target):.6f}",
        "mae": f"{mae(image, target):.6f}",
        "psnr": f"{psnr(image, target):.6f}",
        "ssim": f"{ssim(image, target):.6f}",
        "delta_e": f"{delta_e(image, target):.6f}",
        "entropy": f"{entropy(image):.6f}",
    }


if __name__ == "__main__":
    main()
