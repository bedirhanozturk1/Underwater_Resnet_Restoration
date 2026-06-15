from __future__ import annotations

import torch
from torch import nn

from src.models.diffusion import DiffusionSchedule


@torch.no_grad()
def sample_conditioned_image(
    model: nn.Module,
    condition: torch.Tensor,
    schedule: DiffusionSchedule,
    device: torch.device | str,
) -> torch.Tensor:
    device = torch.device(device)
    model.eval()
    condition = condition.to(device)
    image = torch.randn_like(condition, device=device)

    for step in reversed(range(schedule.timesteps)):
        timestep = torch.full((condition.shape[0],), step, dtype=torch.long, device=device)
        predicted_noise = model(image, condition, timestep)
        beta_t = schedule.betas[step].reshape(1, 1, 1, 1)
        alpha_t = schedule.alphas[step].reshape(1, 1, 1, 1)
        alpha_cumprod_t = schedule.alpha_cumprod[step].reshape(1, 1, 1, 1)

        mean = (image - (beta_t / torch.sqrt(1.0 - alpha_cumprod_t)) * predicted_noise) / torch.sqrt(alpha_t)
        if step > 0:
            image = mean + torch.sqrt(beta_t) * torch.randn_like(image)
        else:
            image = mean

    return image.clamp(-1.0, 1.0)


@torch.no_grad()
def estimate_clean_from_noisy(
    model: nn.Module,
    noisy: torch.Tensor,
    condition: torch.Tensor,
    timesteps: torch.Tensor,
    schedule: DiffusionSchedule,
) -> torch.Tensor:
    predicted_noise = model(noisy, condition, timesteps)
    alpha = schedule.sqrt_alpha_cumprod[timesteps].reshape(timesteps.shape[0], 1, 1, 1)
    sigma = schedule.sqrt_one_minus_alpha_cumprod[timesteps].reshape(timesteps.shape[0], 1, 1, 1)
    return ((noisy - sigma * predicted_noise) / alpha.clamp_min(1e-8)).clamp(-1.0, 1.0)
