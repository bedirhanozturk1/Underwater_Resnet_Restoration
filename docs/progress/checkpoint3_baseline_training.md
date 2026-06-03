# Checkpoint 3: Baseline Training And First Restoration

Status: completed

## Completed

- Conditional U-Net denoising backbone implemented.
- Sinusoidal timestep embedding implemented.
- Diffusion noise prediction loss implemented.
- Single-step training utility implemented.
- Tiny baseline debug training run completed locally.
- Debug checkpoint, loss curve, CSV log, and early restoration grid generated locally.

## Tests / Checks

- `tests/test_unet_forward.py` passed.
- `tests/test_training_step.py` passed.

## Test Result

```text
7 passed
```

## Debug Training Result

Tiny local debug settings:

```text
image size: 64
subset size: 8
batch size: 2
steps: 4
diffusion timesteps: 20
```

Observed losses:

```text
step 1/4 loss=1.154485
step 2/4 loss=1.147803
step 3/4 loss=1.117921
step 4/4 loss=1.121170
```

## Expected Evidence

- `logs/checkpoint3/baseline_debug_training.csv`
- `results/checkpoint3/baseline_loss_curve.png`
- `results/checkpoint3/baseline_early_restoration.png`

The generated logs, checkpoints, and result images are local evidence files and are ignored by Git.

## Next Step

Start Checkpoint 4: implement the ResNet-style residual denoising backbone and compare it with the baseline pipeline.
