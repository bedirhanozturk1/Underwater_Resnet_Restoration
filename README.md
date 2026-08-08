# Underwater ResNet Restoration

This repository implements **Enhancing Diffusion-Based Underwater Image Restoration with Residual Networks**.

The project restores turbid underwater images using a conditional diffusion-based restoration pipeline. The baseline uses a conditional U-Net denoising backbone, and the proposed model uses a ResNet-style residual denoising backbone inside the same diffusion framework.

## Main Task

```text
turbid underwater image -> restored clear/reference image
```

## Completed Comparison

```text
Turbid input
Baseline conditional U-Net diffusion
Proposed residual-backbone diffusion
Parameter-matched U-Net capacity control
```

## Final Result Summary

The final quantitative evaluation uses the fixed 368-image paired test split.

| Experiment | MSE | MAE | PSNR | SSIM | Delta E | Entropy |
|---|---:|---:|---:|---:|---:|---:|
| Baseline U-Net, 128, 50 epoch | 0.039444 | 0.168026 | 15.681501 | 0.610758 | 29.645203 | 5.095362 |
| Parameter-matched U-Net, 128, 50 epoch | 0.034294 | 0.155805 | 16.356273 | 0.746291 | 27.225774 | 4.790907 |
| Residual backbone, 128, 50 epoch | 0.035727 | 0.159895 | 16.304393 | 0.788963 | 26.840257 | 4.368050 |

The residual backbone improves strongly over the default U-Net baseline, especially on SSIM and Delta E. The parameter-matched U-Net control shows that larger U-Net capacity improves MSE, MAE, and PSNR, while the residual backbone remains stronger on SSIM, Delta E, and entropy. See `docs/final_results_summary.md` and `docs/final_report.md` for the final interpretation.

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
5. Full results and ablations
6. Capacity control and qualitative generalization

Details are in `docs/implementation_plan.md`.

## Final Deliverables

Final report materials are generated with:

```bash
python scripts/create_final_deliverables.py
```

The generated local outputs are written to `../final_deliverables/`.

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
