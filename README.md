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

## Full Training On Colab

Upload the prepared Drive folder as:

```text
MyDrive/underwater_resnet_project/
```

Train the baseline model:

```bash
python scripts/train_model.py --model baseline --epochs 50 --batch-size 16
```

Train the residual-backbone model:

```bash
python scripts/train_model.py --model residual --epochs 50 --batch-size 16
```

Resume after a Colab disconnect:

```bash
python scripts/train_model.py --model residual --resume /content/drive/MyDrive/underwater_resnet_project/checkpoints/residual/latest.pth
```

Evaluate a trained checkpoint:

```bash
python scripts/evaluate_model.py --checkpoint /content/drive/MyDrive/underwater_resnet_project/checkpoints/residual/best.pth
```

Run qualitative inference on an image folder:

```bash
python scripts/run_inference.py --checkpoint /content/drive/MyDrive/underwater_resnet_project/checkpoints/residual/best.pth --input-dir /content/drive/MyDrive/underwater_resnet_project/datasets/auxiliary_unpaired/turbidty_from_video_frame --limit 20
```
