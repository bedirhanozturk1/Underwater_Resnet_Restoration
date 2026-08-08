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

## Final Grouped Results

All values below use the grouped held-out split and are reported as mean +/- sample standard deviation across seeds `42`, `123`, and `2026`.

| Experiment | MSE | MAE | PSNR | SSIM | Delta E | Entropy |
|---|---:|---:|---:|---:|---:|---:|
| Default U-Net | 0.039873 +/- 0.001756 | 0.168557 +/- 0.002959 | 15.780514 +/- 0.187075 | 0.657180 +/- 0.015721 | 28.380208 +/- 1.320879 | 4.890910 +/- 0.035327 |
| Parameter-matched U-Net | 0.038056 +/- 0.002727 | 0.164164 +/- 0.005644 | 16.017719 +/- 0.277610 | 0.722221 +/- 0.022096 | 27.590478 +/- 2.280969 | 4.946796 +/- 0.060048 |
| Residual backbone | 0.038782 +/- 0.003119 | 0.166746 +/- 0.006585 | 16.006089 +/- 0.267086 | 0.779948 +/- 0.006607 | 27.053617 +/- 1.081249 | 4.565555 +/- 0.202586 |

The parameter-matched U-Net leads mean MSE, MAE, and PSNR. The residual backbone leads mean SSIM and Delta E. Entropy is retained as a descriptive diagnostic rather than a restoration-quality ranking.

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

To reapply the approved layout to an existing manually edited report without regenerating its text:

```powershell
.\scripts\format_existing_report.ps1 -DocumentPath "..\final_deliverables\final_report_150210321.docx" -PdfPath "..\final_deliverables\final_report_150210321.pdf"
```

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
