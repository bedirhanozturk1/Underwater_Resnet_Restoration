from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F

from src.models.resnet_blocks import ResidualBlock
from src.models.unet import SinusoidalTimeEmbedding


class ResidualUNet(nn.Module):
    def __init__(self, in_channels: int = 6, out_channels: int = 3, base_channels: int = 32, time_dim: int = 128) -> None:
        super().__init__()
        self.time_mlp = nn.Sequential(
            SinusoidalTimeEmbedding(time_dim),
            nn.Linear(time_dim, time_dim),
            nn.SiLU(),
            nn.Linear(time_dim, time_dim),
        )

        self.down1 = ResidualBlock(in_channels, base_channels, time_dim)
        self.down2 = ResidualBlock(base_channels, base_channels * 2, time_dim)
        self.bottleneck1 = ResidualBlock(base_channels * 2, base_channels * 4, time_dim)
        self.bottleneck2 = ResidualBlock(base_channels * 4, base_channels * 4, time_dim)
        self.up2 = ResidualBlock(base_channels * 4 + base_channels * 2, base_channels * 2, time_dim)
        self.up1 = ResidualBlock(base_channels * 2 + base_channels, base_channels, time_dim)
        self.out = nn.Conv2d(base_channels, out_channels, kernel_size=1)

    def forward(self, noisy: torch.Tensor, condition: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        x = torch.cat([noisy, condition], dim=1)
        time_emb = self.time_mlp(timesteps)

        skip1 = self.down1(x, time_emb)
        x = F.avg_pool2d(skip1, kernel_size=2)
        skip2 = self.down2(x, time_emb)
        x = F.avg_pool2d(skip2, kernel_size=2)

        x = self.bottleneck1(x, time_emb)
        x = self.bottleneck2(x, time_emb)

        x = F.interpolate(x, size=skip2.shape[-2:], mode="bilinear", align_corners=False)
        x = self.up2(torch.cat([x, skip2], dim=1), time_emb)
        x = F.interpolate(x, size=skip1.shape[-2:], mode="bilinear", align_corners=False)
        x = self.up1(torch.cat([x, skip1], dim=1), time_emb)
        return self.out(x)
