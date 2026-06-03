# Underwater ResNet Restoration

This repository implements **Enhancing Diffusion-Based Underwater Image Restoration with Residual Networks**.

The project restores turbid underwater images using a conditional diffusion-based restoration pipeline. The baseline uses a conditional U-Net denoising backbone, and the proposed model uses a ResNet-style residual denoising backbone inside the same diffusion framework.

## Main Task

```text
turbid underwater image -> restored clear/reference image
```

## Planned Comparison

```text
Turbid input
Baseline conditional U-Net diffusion
Proposed residual-backbone diffusion
```

## Repository Layout

```text
configs/        training configuration files
docs/           implementation plan and progress notes
notebooks/      Colab workflow notebook
scripts/        runnable checkpoint/training/evaluation scripts
src/            reusable implementation code
tests/          lightweight sanity tests
```

Datasets, checkpoints, logs, and generated results should stay outside GitHub, preferably in Google Drive.

## Progress Checkpoints

1. Dataset and project setup
2. DataLoader and diffusion sanity tests
3. Baseline training and first restoration
4. Residual backbone and final comparison

Details are in `docs/implementation_plan.md`.

## Development Setup

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest tests
```

## Data Policy

Do not commit dataset archives, extracted datasets, checkpoints, logs, or generated result folders.
