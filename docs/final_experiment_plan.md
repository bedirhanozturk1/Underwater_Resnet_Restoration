# Final Experiment Plan

This document freezes the remaining experimental work before final report writing.

## Completed Experiments

| Experiment | Model | Image Size | Epochs | Purpose |
|---|---|---:|---:|---|
| Main baseline | Conditional U-Net | 128 | 50 | Establish baseline diffusion restoration performance |
| Main proposed | ResNet-style residual backbone | 128 | 50 | Test residual denoising backbone contribution |
| Extended baseline | Conditional U-Net | 128 | 100 | Check effect of longer training |
| Extended proposed | ResNet-style residual backbone | 128 | 100 | Check residual convergence after longer training |
| Resolution baseline | Conditional U-Net | 256 | 50 | Test higher-resolution training |
| Resolution proposed | ResNet-style residual backbone | 256 | 50 | Test residual model under higher-resolution training |
| Qualitative generalization | Residual backbone | 128 | inference | Apply model to unpaired turbid images and video-derived frames |

## Parameter-Matched Capacity Control

This experiment checks whether the residual model improvement comes only from having more parameters.

Parameter counts:

```text
Conditional U-Net, base_channels=32: 548067 parameters
Conditional U-Net, base_channels=42: 901797 parameters
Residual backbone, base_channels=32: 886371 parameters
```

Use `base_channels=42` for the parameter-matched U-Net because it is closest to the residual model parameter count.

Status: completed.

## Colab Command: Train Parameter-Matched U-Net

```bash
python scripts/train_model.py \
  --model baseline \
  --epochs 50 \
  --batch-size 16 \
  --image-size 128 \
  --base-channels 42 \
  --print-every 10 \
  --clear-dir /content/drive/MyDrive/underwater_resnet_project/datasets/clear_underwater_color_patch/canon_patch \
  --turbid-dir /content/drive/MyDrive/underwater_resnet_project/datasets/turbidty_underwater_color_patch \
  --split-dir /content/drive/MyDrive/underwater_resnet_project/splits \
  --checkpoint-dir /content/drive/MyDrive/underwater_resnet_project/experiments/param_matched_unet/checkpoints \
  --log-dir /content/drive/MyDrive/underwater_resnet_project/experiments/param_matched_unet/logs
```

## Colab Command: Evaluate Parameter-Matched U-Net

```bash
python scripts/evaluate_model.py \
  --checkpoint /content/drive/MyDrive/underwater_resnet_project/experiments/param_matched_unet/checkpoints/baseline/best.pth \
  --clear-dir /content/drive/MyDrive/underwater_resnet_project/datasets/clear_underwater_color_patch/canon_patch \
  --turbid-dir /content/drive/MyDrive/underwater_resnet_project/datasets/turbidty_underwater_color_patch \
  --split-file /content/drive/MyDrive/underwater_resnet_project/splits/test.txt \
  --result-dir /content/drive/MyDrive/underwater_resnet_project/experiments/param_matched_unet/results/baseline_full
```

## Final Result Summary

Full test-set results were computed on 368 paired test images.

| Experiment | MSE | MAE | PSNR | SSIM | Delta E | Entropy |
|---|---:|---:|---:|---:|---:|---:|
| Baseline U-Net, 128, 50 epoch | 0.039444 | 0.168026 | 15.681501 | 0.610758 | 29.645203 | 5.095362 |
| Parameter-matched U-Net, 128, 50 epoch | 0.034294 | 0.155805 | 16.356273 | 0.746291 | 27.225774 | 4.790907 |
| Residual backbone, 128, 50 epoch | 0.035727 | 0.159895 | 16.304393 | 0.788963 | 26.840257 | 4.368050 |
| Baseline U-Net, 128, 100 epoch | 0.037111 | 0.163163 | 15.976561 | 0.623376 | 28.571008 | 4.943213 |
| Residual backbone, 128, 100 epoch | 0.035936 | 0.160301 | 16.352538 | 0.785447 | 26.866293 | 4.710935 |
| Baseline U-Net, 256, 50 epoch | 0.039126 | 0.167594 | 15.749889 | 0.609380 | 29.117468 | 4.873310 |
| Residual backbone, 256, 50 epoch | 0.039173 | 0.168835 | 15.900427 | 0.807967 | 27.078848 | 4.667301 |

Key interpretation:

- The residual backbone strongly improves over the standard U-Net baseline at the same default capacity.
- The parameter-matched U-Net is stronger than the standard U-Net and slightly better than the residual model on MSE, MAE, and PSNR.
- The residual model remains better than the parameter-matched U-Net on SSIM, Delta E, and entropy, suggesting better structural consistency, color difference, and lower noisy texture.
- Therefore, the final claim should not overstate that the residual backbone is universally better on every metric. The correct claim is that residual blocks improve structural/color-oriented restoration behavior, while increased U-Net capacity can improve pixel-wise metrics.

## Final Reporting Decision

Stop training and move to final reporting. The report should include:

- backbone ablation: standard U-Net vs residual backbone
- capacity control: parameter-matched U-Net vs residual backbone
- extended training: 50 vs 100 epochs
- resolution ablation: 128 vs 256
- qualitative generalization on unpaired/video-derived data
- limitations and failure analysis
