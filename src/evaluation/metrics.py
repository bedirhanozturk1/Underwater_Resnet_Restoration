from __future__ import annotations

import math

import numpy as np
import torch
from skimage.color import rgb2lab
from skimage.metrics import structural_similarity


def mse(prediction: torch.Tensor, target: torch.Tensor) -> float:
    return float(torch.mean((prediction - target) ** 2).detach().cpu().item())


def mae(prediction: torch.Tensor, target: torch.Tensor) -> float:
    return float(torch.mean(torch.abs(prediction - target)).detach().cpu().item())


def psnr(prediction: torch.Tensor, target: torch.Tensor, data_range: float = 1.0) -> float:
    value = mse(prediction, target)
    if value == 0:
        return float("inf")
    return 20.0 * math.log10(data_range) - 10.0 * math.log10(value)


def ssim(prediction: torch.Tensor, target: torch.Tensor, data_range: float = 1.0) -> float:
    pred = _to_numpy_image(prediction)
    ref = _to_numpy_image(target)
    return float(structural_similarity(ref, pred, channel_axis=-1, data_range=data_range))


def delta_e(prediction: torch.Tensor, target: torch.Tensor) -> float:
    pred_lab = rgb2lab(_to_numpy_image(prediction).clip(0.0, 1.0))
    ref_lab = rgb2lab(_to_numpy_image(target).clip(0.0, 1.0))
    return float(np.mean(np.linalg.norm(pred_lab - ref_lab, axis=-1)))


def entropy(image: torch.Tensor, bins: int = 256) -> float:
    values = _to_numpy_image(image).clip(0.0, 1.0).reshape(-1)
    hist, _ = np.histogram(values, bins=bins, range=(0.0, 1.0), density=False)
    probabilities = hist.astype(np.float64) / max(hist.sum(), 1)
    probabilities = probabilities[probabilities > 0]
    return float(-np.sum(probabilities * np.log2(probabilities)))


def _to_numpy_image(tensor: torch.Tensor) -> np.ndarray:
    if tensor.ndim == 4:
        tensor = tensor[0]
    if tensor.ndim != 3:
        raise ValueError("Expected tensor shape [C, H, W] or [B, C, H, W]")
    return tensor.detach().cpu().float().clamp(0.0, 1.0).permute(1, 2, 0).numpy()
