# Checkpoint 4: Residual Backbone And Final Comparison

Status: completed for debug pipeline validation

## Completed

- ResNet-style residual block implemented.
- Residual denoising backbone implemented with the same interface as the baseline U-Net.
- Parameter comparison generated locally.
- Evaluation metrics implemented: MSE, MAE, PSNR, SSIM, Delta E, and entropy.
- Tiny residual debug training run completed locally.
- Debug comparison grid and metrics CSV generated locally.

## Tests / Checks

- `tests/test_residual_forward.py` passed.
- `tests/test_metrics.py` passed.

## Test Result

```text
11 passed
```

## Model Parameter Comparison

```text
Baseline Conditional U-Net parameters: 138099
Residual denoising backbone parameters: 223027
```

## Residual Debug Training Result

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
residual step 1/4 loss=1.218544
residual step 2/4 loss=1.138745
residual step 3/4 loss=1.115120
residual step 4/4 loss=1.104735
```

## Debug Metric Output

These metrics are from a tiny debug run and validate the evaluation pipeline. They are not final model-quality results.

```text
Method                    MSE       MAE       PSNR      SSIM      Delta E    Entropy
Turbid input              0.062202  0.246232  12.061947 0.684129  28.775528  4.130469
Baseline U-Net debug      0.051622  0.181896  12.871620 0.022640  48.441261  7.023406
Residual backbone debug   0.041320  0.167421  13.838395 0.027179  44.757538  6.590255
```

## Expected Evidence

- `results/checkpoint4/model_parameter_comparison.txt`
- `results/checkpoint4/final_metrics.csv`
- `results/checkpoint4/final_comparison_grid.png`
- `results/checkpoint4/training_curves.png`

The generated logs, checkpoints, metrics, and result images are local evidence files and are ignored by Git.

## Next Step

Move to full training workflow on Colab/A100, using the same baseline and residual model interfaces.
