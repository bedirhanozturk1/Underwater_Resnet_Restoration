# Checkpoint 2: DataLoader And Diffusion Sanity Tests

Status: completed

## Completed

- Paired PyTorch dataset implemented.
- Image resizing and normalization to `[-1, 1]` implemented.
- DataLoader sanity visualization generated locally.
- Linear diffusion noise schedule implemented.
- Forward diffusion sampling implemented.
- Forward diffusion timestep visualization generated locally.

## Tests / Checks

- `tests/test_dataloader.py` passed.
- `tests/test_diffusion.py` passed.

## DataLoader Verification Result

```text
Dataset size: 2937
Batch turbid shape: (4, 3, 128, 128)
Batch clear shape: (4, 3, 128, 128)
Tensor min/max: -0.9765, 0.3882
```

## Test Result

```text
5 passed
```

## Expected Evidence

- `results/checkpoint2/sample_batch.png`
- `results/checkpoint2/forward_diffusion_grid.png`

These files are generated locally and ignored by Git because result files should not be committed to the repository.

## Next Step

Start Checkpoint 3: implement the baseline conditional U-Net diffusion model and run a small debug training loop.
