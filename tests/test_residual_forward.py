import torch

from src.models.residual_unet import ResidualUNet
from src.models.resnet_blocks import ResidualBlock, count_parameters


def test_residual_block_preserves_requested_shape() -> None:
    block = ResidualBlock(in_channels=4, out_channels=8, time_dim=16)
    x = torch.randn(2, 4, 16, 16)
    time_emb = torch.randn(2, 16)

    output = block(x, time_emb)

    assert output.shape == (2, 8, 16, 16)
    assert torch.isfinite(output).all()


def test_residual_unet_forward_shape() -> None:
    model = ResidualUNet(base_channels=8, time_dim=32)
    noisy = torch.randn(2, 3, 32, 32)
    condition = torch.randn(2, 3, 32, 32)
    timesteps = torch.tensor([0, 5], dtype=torch.long)

    output = model(noisy, condition, timesteps)

    assert output.shape == noisy.shape
    assert torch.isfinite(output).all()
    assert count_parameters(model) > 0
