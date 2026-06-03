import torch

from src.models.diffusion import DiffusionSchedule, linear_beta_schedule


def test_linear_beta_schedule_has_expected_shape_and_range() -> None:
    betas = linear_beta_schedule(10)

    assert betas.shape == (10,)
    assert torch.all(betas > 0)
    assert torch.all(betas < 1)
    assert betas[0] < betas[-1]


def test_q_sample_keeps_shape_and_uses_timestep_strength() -> None:
    schedule = DiffusionSchedule(timesteps=100)
    x_start = torch.ones(2, 3, 16, 16)
    noise = torch.ones_like(x_start)

    early, returned_noise = schedule.q_sample(x_start, torch.tensor([0, 0]), noise=noise)
    late, _ = schedule.q_sample(x_start, torch.tensor([99, 99]), noise=noise)

    assert early.shape == x_start.shape
    assert late.shape == x_start.shape
    assert torch.equal(returned_noise, noise)
    assert torch.mean(torch.abs(late - x_start)) > torch.mean(torch.abs(early - x_start))
