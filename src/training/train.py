from __future__ import annotations

import torch
from torch import nn

from src.models.diffusion import DiffusionSchedule
from src.training.losses import noise_prediction_loss


def diffusion_training_step(
    model: nn.Module,
    batch: dict[str, torch.Tensor],
    schedule: DiffusionSchedule,
    optimizer: torch.optim.Optimizer,
    device: torch.device | str = "cpu",
) -> float:
    device = torch.device(device)
    model.train()
    clear = batch["clear"].to(device)
    turbid = batch["turbid"].to(device)
    timesteps = torch.randint(0, schedule.timesteps, (clear.shape[0],), device=device)
    noisy, noise = schedule.q_sample(clear, timesteps)

    predicted_noise = model(noisy, turbid, timesteps)
    loss = noise_prediction_loss(predicted_noise, noise)

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
    return float(loss.detach().cpu().item())
