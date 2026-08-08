# Final Results Summary

> **Superseded:** The values in this document use the original filename-random split. A later audit found source-chart overlap and exact-pair duplicates across partitions. Do not cite these values as final evidence. Replacement `grouped_v1_contiguous_24` results will be reported as mean and sample standard deviation across seeds 42, 123, and 2026.

This document summarizes the frozen experimental results for the final report.

## Completed Experiments

| Experiment | Model | Image Size | Epochs | Purpose |
|---|---|---:|---:|---|
| Main baseline | Conditional U-Net | 128 | 50 | Standard diffusion denoising backbone |
| Main proposed | ResNet-style residual backbone | 128 | 50 | Proposed residual denoising backbone |
| Capacity control | Parameter-matched U-Net | 128 | 50 | Check whether gains come from parameter count |
| Extended training | Conditional U-Net / residual | 128 | 100 | Check longer training behavior |
| Resolution ablation | Conditional U-Net / residual | 256 | 50 | Check higher-resolution behavior |
| Qualitative generalization | Residual backbone | 128 | inference | Test unpaired/video-derived data qualitatively |

## Full Test Metrics

All quantitative results below are evaluated on the 368-image paired test split.

| Experiment | MSE | MAE | PSNR | SSIM | Delta E | Entropy |
|---|---:|---:|---:|---:|---:|---:|
| Baseline U-Net, 128, 50 epoch | 0.039444 | 0.168026 | 15.681501 | 0.610758 | 29.645203 | 5.095362 |
| Parameter-matched U-Net, 128, 50 epoch | 0.034294 | 0.155805 | 16.356273 | 0.746291 | 27.225774 | 4.790907 |
| Residual backbone, 128, 50 epoch | 0.035727 | 0.159895 | 16.304393 | 0.788963 | 26.840257 | 4.368050 |
| Baseline U-Net, 128, 100 epoch | 0.037111 | 0.163163 | 15.976561 | 0.623376 | 28.571008 | 4.943213 |
| Residual backbone, 128, 100 epoch | 0.035936 | 0.160301 | 16.352538 | 0.785447 | 26.866293 | 4.710935 |
| Baseline U-Net, 256, 50 epoch | 0.039126 | 0.167594 | 15.749889 | 0.609380 | 29.117468 | 4.873310 |
| Residual backbone, 256, 50 epoch | 0.039173 | 0.168835 | 15.900427 | 0.807967 | 27.078848 | 4.667301 |

## Interpretation

The proposed residual backbone clearly improves over the default U-Net baseline at the same training configuration. At 128x128 and 50 epochs, the residual model reduces MSE by 9.42%, increases PSNR by 0.62 dB, increases SSIM by 29.18%, and reduces Delta E by 9.46% compared with the default U-Net baseline.

The parameter-matched U-Net capacity control changes the interpretation. Increasing U-Net capacity improves pixel-wise metrics and gives slightly better MSE, MAE, and PSNR than the residual model. However, the residual model remains better on SSIM, Delta E, and entropy. This suggests that the residual backbone is especially useful for preserving structural consistency and reducing noisy/color artifacts, while increased U-Net capacity helps pixel-wise reconstruction.

The 100-epoch experiment shows that longer training improves the baseline, while the residual model already reaches strong performance by 50 epochs and does not improve consistently with additional epochs. The 256-resolution experiment improves residual SSIM but does not improve all pixel-wise metrics, showing that higher resolution alone is not sufficient without further tuning.

## Final Claim

The final report should claim a controlled improvement in structural and color-oriented restoration behavior, not universal dominance on every metric:

```text
Replacing the default conditional U-Net denoising backbone with a ResNet-style residual backbone improves structural similarity, color-difference behavior, and output smoothness compared with the default baseline. A parameter-matched U-Net capacity control shows that some pixel-wise improvements can also be obtained by increasing model capacity, while the residual backbone remains stronger on SSIM, Delta E, and entropy.
```

## Limitations

- Cross-dataset inference is qualitative only because the external/unpaired datasets do not provide paired clear references.
- The model is trained mainly on paired color-patch images, so generalization to non-patch underwater scenes is limited.
- The output often improves structure and smoothness but does not fully recover target clear colors.
- The current model is image-based and does not implement temporal video restoration.
