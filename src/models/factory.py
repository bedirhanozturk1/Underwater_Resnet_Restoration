from __future__ import annotations

from torch import nn

from src.models.residual_unet import ResidualUNet
from src.models.unet import ConditionalUNet


def build_model(model_name: str, base_channels: int = 32, time_dim: int = 128) -> nn.Module:
    if model_name == "baseline":
        return ConditionalUNet(base_channels=base_channels, time_dim=time_dim)
    if model_name == "residual":
        return ResidualUNet(base_channels=base_channels, time_dim=time_dim)
    raise ValueError(f"Unknown model name: {model_name}")
