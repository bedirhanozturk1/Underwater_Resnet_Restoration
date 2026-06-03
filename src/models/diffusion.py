from __future__ import annotations

import torch


def linear_beta_schedule(timesteps: int, beta_start: float = 1e-4, beta_end: float = 0.02) -> torch.Tensor:
    if timesteps <= 0:
        raise ValueError("timesteps must be positive")
    return torch.linspace(beta_start, beta_end, timesteps, dtype=torch.float32)


class DiffusionSchedule:
    def __init__(self, timesteps: int, device: torch.device | str = "cpu") -> None:
        self.timesteps = timesteps
        self.device = torch.device(device)

        betas = linear_beta_schedule(timesteps).to(self.device)
        alphas = 1.0 - betas
        alpha_cumprod = torch.cumprod(alphas, dim=0)

        self.betas = betas
        self.alphas = alphas
        self.alpha_cumprod = alpha_cumprod
        self.sqrt_alpha_cumprod = torch.sqrt(alpha_cumprod)
        self.sqrt_one_minus_alpha_cumprod = torch.sqrt(1.0 - alpha_cumprod)

    def q_sample(
        self,
        x_start: torch.Tensor,
        t: torch.Tensor,
        noise: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if noise is None:
            noise = torch.randn_like(x_start)
        if t.ndim != 1 or t.shape[0] != x_start.shape[0]:
            raise ValueError("t must have shape [batch_size]")

        sqrt_alpha = _extract(self.sqrt_alpha_cumprod, t, x_start.shape)
        sqrt_one_minus_alpha = _extract(self.sqrt_one_minus_alpha_cumprod, t, x_start.shape)
        return sqrt_alpha * x_start + sqrt_one_minus_alpha * noise, noise


def _extract(values: torch.Tensor, timesteps: torch.Tensor, target_shape: torch.Size) -> torch.Tensor:
    gathered = values.gather(0, timesteps.to(values.device))
    return gathered.reshape(timesteps.shape[0], *((1,) * (len(target_shape) - 1)))
