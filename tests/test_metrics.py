import math

import torch

from src.evaluation.metrics import delta_e, entropy, mae, mse, psnr, ssim


def test_full_reference_metrics_are_finite_for_similar_images() -> None:
    target = torch.full((3, 32, 32), 0.5)
    prediction = target + 0.05

    assert mse(prediction, target) > 0
    assert mae(prediction, target) > 0
    assert math.isfinite(psnr(prediction, target))
    assert math.isfinite(ssim(prediction, target))
    assert math.isfinite(delta_e(prediction, target))


def test_entropy_is_non_negative() -> None:
    image = torch.rand(3, 32, 32)

    assert entropy(image) >= 0
