import torch

from src.models.diffusion import DiffusionSchedule
from src.models.unet import ConditionalUNet
from src.training.train import diffusion_training_step


def test_diffusion_training_step_returns_finite_loss() -> None:
    model = ConditionalUNet(base_channels=8, time_dim=32)
    schedule = DiffusionSchedule(timesteps=10)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    batch = {
        "clear": torch.randn(2, 3, 32, 32),
        "turbid": torch.randn(2, 3, 32, 32),
    }

    loss = diffusion_training_step(model, batch, schedule, optimizer)

    assert isinstance(loss, float)
    assert loss > 0
    assert torch.isfinite(torch.tensor(loss))
