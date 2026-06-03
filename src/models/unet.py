from __future__ import annotations

import math

import torch
from torch import nn
import torch.nn.functional as F


class SinusoidalTimeEmbedding(nn.Module):
    def __init__(self, dim: int) -> None:
        super().__init__()
        self.dim = dim

    def forward(self, timesteps: torch.Tensor) -> torch.Tensor:
        half_dim = self.dim // 2
        exponent = -math.log(10000.0) * torch.arange(half_dim, device=timesteps.device) / max(half_dim - 1, 1)
        freqs = torch.exp(exponent)
        args = timesteps.float().unsqueeze(1) * freqs.unsqueeze(0)
        embedding = torch.cat([torch.sin(args), torch.cos(args)], dim=1)
        if self.dim % 2 == 1:
            embedding = F.pad(embedding, (0, 1))
        return embedding


class ConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, time_dim: int) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.time_proj = nn.Linear(time_dim, out_channels)
        self.norm1 = nn.GroupNorm(_groups(out_channels), out_channels)
        self.norm2 = nn.GroupNorm(_groups(out_channels), out_channels)
        self.act = nn.SiLU()

    def forward(self, x: torch.Tensor, time_emb: torch.Tensor) -> torch.Tensor:
        x = self.act(self.norm1(self.conv1(x)))
        x = x + self.time_proj(time_emb).unsqueeze(-1).unsqueeze(-1)
        x = self.act(self.norm2(self.conv2(x)))
        return x


class ConditionalUNet(nn.Module):
    def __init__(self, in_channels: int = 6, out_channels: int = 3, base_channels: int = 32, time_dim: int = 128) -> None:
        super().__init__()
        self.time_mlp = nn.Sequential(
            SinusoidalTimeEmbedding(time_dim),
            nn.Linear(time_dim, time_dim),
            nn.SiLU(),
            nn.Linear(time_dim, time_dim),
        )

        self.down1 = ConvBlock(in_channels, base_channels, time_dim)
        self.down2 = ConvBlock(base_channels, base_channels * 2, time_dim)
        self.bottleneck = ConvBlock(base_channels * 2, base_channels * 4, time_dim)
        self.up2 = ConvBlock(base_channels * 4 + base_channels * 2, base_channels * 2, time_dim)
        self.up1 = ConvBlock(base_channels * 2 + base_channels, base_channels, time_dim)
        self.out = nn.Conv2d(base_channels, out_channels, kernel_size=1)

    def forward(self, noisy: torch.Tensor, condition: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        x = torch.cat([noisy, condition], dim=1)
        time_emb = self.time_mlp(timesteps)

        skip1 = self.down1(x, time_emb)
        x = F.avg_pool2d(skip1, kernel_size=2)
        skip2 = self.down2(x, time_emb)
        x = F.avg_pool2d(skip2, kernel_size=2)

        x = self.bottleneck(x, time_emb)

        x = F.interpolate(x, size=skip2.shape[-2:], mode="bilinear", align_corners=False)
        x = self.up2(torch.cat([x, skip2], dim=1), time_emb)
        x = F.interpolate(x, size=skip1.shape[-2:], mode="bilinear", align_corners=False)
        x = self.up1(torch.cat([x, skip1], dim=1), time_emb)
        return self.out(x)


def _groups(channels: int) -> int:
    for groups in (8, 4, 2):
        if channels % groups == 0:
            return groups
    return 1
