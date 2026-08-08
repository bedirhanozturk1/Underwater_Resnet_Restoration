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

## Remaining Required Experiment

The only remaining experiment is a parameter-matched U-Net capacity control. It checks whether the residual model improvement comes only from having more parameters.

Parameter counts:

```text
Conditional U-Net, base_channels=32: 548067 parameters
Conditional U-Net, base_channels=42: 901797 parameters
Residual backbone, base_channels=32: 886371 parameters
```

Use `base_channels=42` for the parameter-matched U-Net because it is closest to the residual model parameter count.

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

## Final Reporting Decision

After this experiment, stop training and move to final reporting. The report should include:

- backbone ablation: standard U-Net vs residual backbone
- capacity control: parameter-matched U-Net vs residual backbone
- extended training: 50 vs 100 epochs
- resolution ablation: 128 vs 256
- qualitative generalization on unpaired/video-derived data
- limitations and failure analysis
