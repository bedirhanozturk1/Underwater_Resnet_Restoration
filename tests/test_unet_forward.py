import torch

from src.models.unet import ConditionalUNet


def test_conditional_unet_forward_shape() -> None:
    model = ConditionalUNet(base_channels=8, time_dim=32)
    noisy = torch.randn(2, 3, 32, 32)
    condition = torch.randn(2, 3, 32, 32)
    timesteps = torch.tensor([0, 5], dtype=torch.long)

    output = model(noisy, condition, timesteps)

    assert output.shape == noisy.shape
    assert torch.isfinite(output).all()
