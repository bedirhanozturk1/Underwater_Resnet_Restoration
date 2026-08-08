from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Subset

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.dataset import UnderwaterPairedDataset, denormalize_image
from src.evaluation.metrics import delta_e, entropy, mae, mse, psnr, ssim
from src.models.diffusion import DiffusionSchedule
from src.models.factory import build_model
from src.models.sampling import sample_conditioned_image
from src.utils.image_io import save_labeled_grid, tensor_to_pil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a trained conditional diffusion restoration model.")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--run-name", default=None, help="Unique output prefix; defaults to checkpoint run_name.")
    parser.add_argument("--seed", type=int, default=2026, help="Fixed reverse-sampling seed.")
    parser.add_argument("--clear-dir", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/datasets/clear_underwater_color_patch/canon_patch"))
    parser.add_argument("--turbid-dir", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/datasets/turbidty_underwater_color_patch"))
    parser.add_argument("--split-file", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/splits/test.txt"))
    parser.add_argument("--result-dir", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/results/evaluation"))
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--grid-samples", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = build_model(checkpoint["model"], checkpoint["base_channels"], checkpoint["time_dim"]).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    schedule = DiffusionSchedule(int(checkpoint["timesteps"]), device=device)

    dataset = UnderwaterPairedDataset(args.clear_dir, args.turbid_dir, args.split_file, image_size=int(checkpoint["image_size"]))
    if args.limit > 0:
        dataset = Subset(dataset, list(range(min(args.limit, len(dataset)))))
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)

    args.result_dir.mkdir(parents=True, exist_ok=True)
    run_name = args.run_name or checkpoint.get("run_name") or checkpoint["model"]
    rows = []
    grid_images = []
    for batch in loader:
        clear = batch["clear"].to(device)
        turbid = batch["turbid"].to(device)
        restored = sample_conditioned_image(model, turbid, schedule, device)
        for idx in range(clear.shape[0]):
            filename = batch["filename"][idx]
            clear_img = denormalize_image(clear[idx].cpu())
            turbid_img = denormalize_image(turbid[idx].cpu())
            restored_img = denormalize_image(restored[idx].cpu())
            rows.append(_metric_row(filename, restored_img, clear_img))
            if len(grid_images) < args.grid_samples * 3:
                grid_images.extend([
                    (f"{filename} turbid", tensor_to_pil(turbid_img)),
                    (f"{filename} restored", tensor_to_pil(restored_img)),
                    (f"{filename} clear", tensor_to_pil(clear_img)),
                ])

    if not rows:
        raise ValueError("Evaluation split produced no metric rows")
    metrics_path = args.result_dir / f"{run_name}_metrics.csv"
    with metrics_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    if grid_images:
        save_labeled_grid(grid_images, args.result_dir / f"{run_name}_comparison_grid.png", columns=3)
    manifest = {
        "run_name": run_name,
        "training_seed": checkpoint.get("seed"),
        "evaluation_seed": args.seed,
        "split_id": checkpoint.get("split_id", "unspecified"),
        "split_file": str(args.split_file),
        "checkpoint": str(args.checkpoint),
        "model": checkpoint["model"],
        "base_channels": checkpoint["base_channels"],
        "image_size": checkpoint["image_size"],
        "timesteps": checkpoint["timesteps"],
        "n": len(rows),
    }
    (args.result_dir / f"{run_name}_evaluation_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote metrics to {metrics_path}")


def _metric_row(filename: str, image: torch.Tensor, target: torch.Tensor) -> dict[str, str]:
    return {
        "filename": filename,
        "mse": f"{mse(image, target):.6f}",
        "mae": f"{mae(image, target):.6f}",
        "psnr": f"{psnr(image, target):.6f}",
        "ssim": f"{ssim(image, target):.6f}",
        "delta_e_cie76": f"{delta_e(image, target):.6f}",
        "entropy": f"{entropy(image):.6f}",
    }


if __name__ == "__main__":
    main()
