from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.dataset import UnderwaterPairedDataset
from src.models.diffusion import DiffusionSchedule
from src.models.factory import build_model
from src.training.losses import noise_prediction_loss


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a baseline or residual conditional diffusion denoising model.")
    parser.add_argument("--model", choices=("baseline", "residual"), required=True)
    parser.add_argument("--run-name", default=None, help="Unique output name; defaults to the model name.")
    parser.add_argument("--split-id", default="unspecified")
    parser.add_argument("--clear-dir", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/datasets/clear_underwater_color_patch/canon_patch"))
    parser.add_argument("--turbid-dir", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/datasets/turbidty_underwater_color_patch"))
    parser.add_argument("--split-dir", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/splits"))
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/checkpoints"))
    parser.add_argument("--log-dir", type=Path, default=Path("/content/drive/MyDrive/underwater_resnet_project/logs"))
    parser.add_argument("--image-size", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--timesteps", type=int, default=100)
    parser.add_argument("--base-channels", type=int, default=32)
    parser.add_argument("--time-dim", type=int, default=128)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume", type=Path, default=None)
    parser.add_argument("--print-every", type=int, default=20, help="Print progress every N batches.")
    parser.add_argument("--max-train-batches", type=int, default=0, help="Optional debug limit; 0 means full epoch.")
    parser.add_argument("--max-val-batches", type=int, default=0, help="Optional debug limit; 0 means full validation.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    run_name = args.run_name or args.model
    run_checkpoint_dir = args.checkpoint_dir / run_name
    run_log_dir = args.log_dir / run_name
    run_checkpoint_dir.mkdir(parents=True, exist_ok=True)
    run_log_dir.mkdir(parents=True, exist_ok=True)

    train_loader = _make_loader(args, "train", shuffle=True)
    val_loader = _make_loader(args, "val", shuffle=False)
    model = build_model(args.model, base_channels=args.base_channels, time_dim=args.time_dim).to(device)
    schedule = DiffusionSchedule(args.timesteps, device=device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    start_epoch = 1
    best_val_loss = float("inf")
    if args.resume is not None:
        checkpoint = torch.load(args.resume, map_location=device, weights_only=False)
        expected_metadata = {
            "model": args.model,
            "run_name": run_name,
            "seed": args.seed,
            "split_id": args.split_id,
            "image_size": args.image_size,
            "timesteps": args.timesteps,
            "base_channels": args.base_channels,
        }
        mismatches = {
            key: (checkpoint.get(key), expected)
            for key, expected in expected_metadata.items()
            if checkpoint.get(key) != expected
        }
        if mismatches:
            raise ValueError(f"Resume checkpoint metadata does not match this run: {mismatches}")
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        start_epoch = int(checkpoint["epoch"]) + 1
        best_val_loss = float(checkpoint.get("best_val_loss", best_val_loss))
        if "python_random_state" in checkpoint:
            random.setstate(checkpoint["python_random_state"])
        if "numpy_random_state" in checkpoint:
            np.random.set_state(checkpoint["numpy_random_state"])
        if "torch_rng_state" in checkpoint:
            torch.set_rng_state(checkpoint["torch_rng_state"])
        if torch.cuda.is_available() and checkpoint.get("cuda_rng_states") is not None:
            torch.cuda.set_rng_state_all(checkpoint["cuda_rng_states"])
        print(f"Resumed from {args.resume} at epoch {start_epoch}")

    log_path = run_log_dir / "training.csv"
    _ensure_log(log_path)

    for epoch in range(start_epoch, args.epochs + 1):
        print(f"starting epoch {epoch}/{args.epochs}", flush=True)
        train_loss = _run_epoch(
            model,
            train_loader,
            schedule,
            optimizer,
            device,
            train=True,
            max_batches=args.max_train_batches,
            print_every=args.print_every,
            phase="train",
            epoch=epoch,
            epochs=args.epochs,
        )
        val_loss = _run_epoch(
            model,
            val_loader,
            schedule,
            optimizer,
            device,
            train=False,
            max_batches=args.max_val_batches,
            print_every=args.print_every,
            phase="val",
            epoch=epoch,
            epochs=args.epochs,
        )
        is_best = val_loss < best_val_loss
        if is_best:
            best_val_loss = val_loss

        row = {"epoch": epoch, "train_loss": f"{train_loss:.6f}", "val_loss": f"{val_loss:.6f}", "best_val_loss": f"{best_val_loss:.6f}"}
        with log_path.open("a", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=list(row)).writerow(row)

        checkpoint = {
            "model": args.model,
            "run_name": run_name,
            "seed": args.seed,
            "split_id": args.split_id,
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "best_val_loss": best_val_loss,
            "image_size": args.image_size,
            "timesteps": args.timesteps,
            "base_channels": args.base_channels,
            "time_dim": args.time_dim,
            "batch_size": args.batch_size,
            "epochs": args.epochs,
            "learning_rate": args.lr,
            "train_split": str(args.split_dir / "train.txt"),
            "val_split": str(args.split_dir / "val.txt"),
            "python_random_state": random.getstate(),
            "numpy_random_state": np.random.get_state(),
            "torch_rng_state": torch.get_rng_state(),
            "cuda_rng_states": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
        }
        torch.save(checkpoint, run_checkpoint_dir / "latest.pth")
        if is_best:
            torch.save(checkpoint, run_checkpoint_dir / "best.pth")

        print(f"epoch {epoch}/{args.epochs} train_loss={train_loss:.6f} val_loss={val_loss:.6f} best={best_val_loss:.6f}", flush=True)

    completion = {
        "run_name": run_name,
        "model": args.model,
        "seed": args.seed,
        "split_id": args.split_id,
        "epochs": args.epochs,
        "best_val_loss": best_val_loss,
    }
    (run_checkpoint_dir / "completed.json").write_text(
        json.dumps(completion, indent=2) + "\n",
        encoding="utf-8",
    )


def _make_loader(args: argparse.Namespace, split: str, shuffle: bool) -> DataLoader:
    dataset = UnderwaterPairedDataset(
        clear_dir=args.clear_dir,
        turbid_dir=args.turbid_dir,
        split_file=args.split_dir / f"{split}.txt",
        image_size=args.image_size,
        augment=split == "train",
    )
    return DataLoader(dataset, batch_size=args.batch_size, shuffle=shuffle, num_workers=args.num_workers, pin_memory=torch.cuda.is_available())


def _run_epoch(
    model,
    loader,
    schedule,
    optimizer,
    device: torch.device,
    train: bool,
    max_batches: int = 0,
    print_every: int = 20,
    phase: str = "train",
    epoch: int = 0,
    epochs: int = 0,
) -> float:
    model.train(train)
    total_loss = 0.0
    batch_count = 0
    start_time = time.time()
    total_batches = min(len(loader), max_batches) if max_batches > 0 else len(loader)
    for batch in loader:
        if max_batches > 0 and batch_count >= max_batches:
            break
        clear = batch["clear"].to(device)
        turbid = batch["turbid"].to(device)
        timesteps = torch.randint(0, schedule.timesteps, (clear.shape[0],), device=device)
        noisy, noise = schedule.q_sample(clear, timesteps)
        with torch.set_grad_enabled(train):
            predicted_noise = model(noisy, turbid, timesteps)
            loss = noise_prediction_loss(predicted_noise, noise)
            if train:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
        total_loss += float(loss.detach().cpu().item())
        batch_count += 1
        if _should_print_progress(batch_count, total_batches, print_every):
            mean_loss = total_loss / max(batch_count, 1)
            elapsed = time.time() - start_time
            eta = (elapsed / batch_count) * max(total_batches - batch_count, 0)
            percent = 100.0 * batch_count / max(total_batches, 1)
            print(
                f"epoch {epoch}/{epochs} {phase} batch {batch_count}/{total_batches} "
                f"({percent:.1f}%) loss={mean_loss:.6f} elapsed={_format_seconds(elapsed)} eta={_format_seconds(eta)}",
                flush=True,
            )
    return total_loss / max(batch_count, 1)


def _should_print_progress(batch_count: int, total_batches: int, print_every: int) -> bool:
    if print_every <= 0:
        return False
    return batch_count == 1 or batch_count == total_batches or batch_count % print_every == 0


def _format_seconds(seconds: float) -> str:
    seconds = int(max(seconds, 0))
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{sec:02d}s"
    if minutes:
        return f"{minutes}m{sec:02d}s"
    return f"{sec}s"


def _ensure_log(log_path: Path) -> None:
    if log_path.exists():
        return
    with log_path.open("w", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=["epoch", "train_loss", "val_loss", "best_val_loss"]).writeheader()


if __name__ == "__main__":
    main()
