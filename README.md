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

## Superseded Result Summary

The values below came from the original filename-random split. Dataset auditing later found source-chart overlap and exact-pair duplicates across partitions. These values are retained only as historical records and must not be cited as final evidence.

| Experiment | MSE | MAE | PSNR | SSIM | Delta E | Entropy |
|---|---:|---:|---:|---:|---:|---:|
| Baseline U-Net, 128, 50 epoch | 0.039444 | 0.168026 | 15.681501 | 0.610758 | 29.645203 | 5.095362 |
| Parameter-matched U-Net, 128, 50 epoch | 0.034294 | 0.155805 | 16.356273 | 0.746291 | 27.225774 | 4.790907 |
| Residual backbone, 128, 50 epoch | 0.035727 | 0.159895 | 16.304393 | 0.788963 | 26.840257 | 4.368050 |

Replacement experiments use contiguous 24-patch source groups, global exact-pair deduplication, and three training seeds for each of the three principal models. New results will be summarized under the Drive experiment directory after the matrix completes.

## Current Evaluation Protocol

- Split ID: `grouped_v1_contiguous_24`
- Assignment: 122 train groups, 15 validation groups, and 16 test groups
- Counts after exact-pair deduplication: 2,899 train, 357 validation, and 384 test pairs
- Models: default U-Net, parameter-matched U-Net, and residual backbone
- Training seeds: `42`, `123`, and `2026`
- Evaluation sampling seed: `2026`
- Aggregation: mean and sample standard deviation across the three training seeds

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

Supervisor checkpoint documents are available in both Word and PDF form under `docs/supervisor_checkpoints/`.

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

## Grouped 3x3 Training On Colab

Upload the prepared Drive folder as:

```text
MyDrive/underwater_resnet_project/
```

Open `notebooks/colab_training.ipynb`, select a GPU runtime, and run all cells. The notebook invokes:

```bash
python scripts/run_grouped_experiments.py --drive-root /content/drive/MyDrive/underwater_resnet_project
```

The orchestration script creates the grouped split, runs all nine training/evaluation jobs, resumes partial jobs from `latest.pth`, skips completed jobs, and writes aggregate summaries to:

```bash
/content/drive/MyDrive/underwater_resnet_project/experiments/grouped_v1/summaries/
```

Rerun the same command after a Colab disconnect. Completed jobs are not repeated.
