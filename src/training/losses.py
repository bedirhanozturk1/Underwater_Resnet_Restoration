from __future__ import annotations

import torch
import torch.nn.functional as F


def noise_prediction_loss(predicted_noise: torch.Tensor, target_noise: torch.Tensor) -> torch.Tensor:
    return F.mse_loss(predicted_noise, target_noise)
