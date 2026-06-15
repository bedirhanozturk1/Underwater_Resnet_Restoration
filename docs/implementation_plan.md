# Implementation Plan

Project: Enhancing Diffusion-Based Underwater Image Restoration with Residual Networks

This document defines the implementation roadmap for the repository. The project is organized around four progress checkpoints so that implementation progress can be demonstrated clearly to the supervisor without duplicating code across separate weekly folders.

## Objective

The project restores turbid underwater images using a conditional diffusion-based image restoration pipeline.

The baseline model uses a conditional U-Net denoising backbone. The proposed model replaces this backbone with a ResNet-style residual denoising backbone while keeping the same dataset, diffusion process, training pipeline, and evaluation protocol.

Main input-output task:

```text
turbid underwater image -> restored clear/reference image
```

Main comparison:

```text
Turbid input vs baseline conditional U-Net diffusion vs residual-backbone diffusion
```

## Repository Strategy

GitHub stores:

```text
source code
configuration files
tests
scripts
notebooks
documentation
small progress reports
```

Google Drive stores:

```text
datasets
checkpoints
training logs
restored images
metric outputs
large generated figures
```

The full-run entry points are:

```text
scripts/train_model.py --model baseline|residual
scripts/evaluate_model.py
scripts/run_inference.py
```

These scripts are designed for Colab + Google Drive. They save `latest.pth`, `best.pth`, and `training.csv` under the configured Drive checkpoint/log folders and support `--resume` from `latest.pth`.

## Project Structure

```text
Underwater_Resnet_Restoration/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- configs/
|   |-- baseline_unet.yaml
|   `-- residual_backbone.yaml
|-- docs/
|   |-- implementation_plan.md
|   `-- progress/
|       |-- checkpoint1_dataset_setup.md
|       |-- checkpoint2_dataloader_diffusion.md
|       |-- checkpoint3_baseline_training.md
|       `-- checkpoint4_residual_final_comparison.md
|-- notebooks/
|-- scripts/
|-- src/
|   |-- data/
|   |-- models/
|   |-- training/
|   |-- evaluation/
|   `-- utils/
`-- tests/
```

Checkpoint scripts should call reusable code from `src/`. Model, dataset, and metric logic should not be duplicated inside checkpoint-specific files.

## Dataset Strategy

The main supervised training dataset is the paired underwater patch dataset.

Confirmed information from the local dataset inspection:

```text
clear/reference archive: clear_underwater_color_patch.zip
turbid/degraded archive: turbidty_underwater_color_patch.zip
matched image pairs: 3672
missing pairs: 0
pairing key: filename
```

Expected folders after extraction:

```text
clear_underwater_color_patch/canon_patch/*.jpg
turbidty_underwater_color_patch/*.jpg
```

Recommended split:

```text
train: 80%
validation: 10%
test: 10%
```

The split must be filename-based and reproducible using a fixed random seed. Because the paired dataset is patch-based, the implementation should also avoid patch-level leakage where possible. If original scene or source-image identifiers become available, all patches from the same source should be assigned to the same split instead of being distributed across train, validation, and test sets.

The teacher-provided `DATASET CODES DOSYA PAYLASIMI` materials and the referenced Iqbal repository were inspected before the full-training stage. Their videos are used for CLAHE/denoising demos, frame inference, and reconstructed output videos, while the diffusion notebooks/code operate on image folders. This supports keeping the 3672 filename-paired clear/turbid patch images as the supervised training set and using videos/unpaired frames only for qualitative inference or supplementary evidence.

## Model Strategy

The diffusion model is conditional. The turbid image is used as a condition, and the denoising network predicts the noise added to the clear target image.

Training formulation:

```text
condition: turbid image
target: clear image
input to model: noisy clear image x_t concatenated with turbid condition image
output: predicted Gaussian noise
loss: MSE(predicted_noise, actual_noise)
```

Model input/output channels:

```text
input: 6 channels = noisy RGB image + turbid RGB condition
output: 3 channels = predicted RGB noise
```

Baseline:

```text
Conditional U-Net denoising backbone
```

Proposed model:

```text
Conditional ResNet-style residual denoising backbone
```

The proposed model is not a standalone image classifier. It is a conditional diffusion denoising backbone that receives the noisy image, the turbid input condition, and the diffusion timestep embedding. The proposed model should use the same dataset, optimizer, image size, diffusion schedule, loss formulation, and evaluation metrics as the baseline to keep the comparison fair.

## Checkpoint 1: Dataset And Project Setup

Purpose:

```text
Show that the repository, environment, and paired dataset are ready.
```

Implementation tasks:

- Create repository structure.
- Add README, requirements, and ignore rules.
- Implement dataset pair verification.
- Generate reproducible train/validation/test split files.
- Generate a small paired visualization grid.

Tests/checks:

```text
tests/test_dataset_pairs.py
```

Expected evidence:

```text
results/checkpoint1/dataset_report.txt
results/checkpoint1/dataset_pair_samples.png
docs/progress/checkpoint1_dataset_setup.md
```

Supervisor report sentence:

```text
I verified that the dataset contains 3672 matched clear/turbid image pairs with no missing pairs, and I prepared reproducible train/validation/test splits.
```

## Checkpoint 2: DataLoader And Diffusion Sanity Tests

Purpose:

```text
Show that paired images enter the training pipeline correctly and that the forward diffusion process works.
```

Implementation tasks:

- Implement paired PyTorch dataset.
- Implement train/validation/test DataLoaders.
- Implement resizing, tensor conversion, and normalization.
- Implement diffusion noise schedule.
- Implement forward diffusion sampling.
- Generate a visual grid of increasing noise levels.

Tests/checks:

```text
tests/test_dataloader.py
tests/test_diffusion.py
```

Expected evidence:

```text
results/checkpoint2/sample_batch.png
results/checkpoint2/forward_diffusion_grid.png
docs/progress/checkpoint2_dataloader_diffusion.md
```

Supervisor report sentence:

```text
I implemented and tested the paired image DataLoader and the forward diffusion process. The generated visualization shows the target image being gradually corrupted by Gaussian noise over diffusion timesteps.
```

## Checkpoint 3: Baseline Training And First Restoration

Purpose:

```text
Show that the baseline diffusion restoration pipeline works end-to-end.
```

Implementation tasks:

- Implement conditional U-Net denoising model.
- Implement timestep embedding.
- Implement training loop.
- Implement validation loop.
- Implement checkpoint saving and CSV logging.
- Run a small debug training run.
- Generate the first restored output from a checkpoint.

Tests/checks:

```text
tests/test_unet_forward.py
tests/test_training_step.py
```

Expected evidence:

```text
logs/checkpoint3/baseline_debug_training.csv
results/checkpoint3/baseline_loss_curve.png
results/checkpoint3/baseline_early_restoration.png
docs/progress/checkpoint3_baseline_training.md
```

Supervisor report sentence:

```text
I implemented the baseline conditional U-Net diffusion model and completed a small training run. The pipeline can now produce an initial restoration output from a turbid input.
```

## Checkpoint 4: Residual Backbone And Final Comparison

Purpose:

```text
Show the project contribution and final comparison against the baseline.
```

Implementation tasks:

- Implement ResNet-style residual blocks.
- Implement residual denoising backbone.
- Verify residual model forward pass.
- Train residual model under the same pipeline as the baseline.
- Evaluate turbid input, baseline output, and residual model output.
- Generate final metric tables and qualitative comparison grids.

Tests/checks:

```text
tests/test_residual_forward.py
tests/test_metrics.py
```

Expected evidence:

```text
results/checkpoint4/model_parameter_comparison.txt
results/checkpoint4/final_metrics.csv
results/checkpoint4/final_comparison_grid.png
results/checkpoint4/training_curves.png
docs/progress/checkpoint4_residual_final_comparison.md
```

Supervisor report sentence:

```text
I implemented the ResNet-style residual denoising backbone and compared it against the baseline U-Net diffusion model using the same dataset, training pipeline, and evaluation metrics.
```

## Planned Tests

```text
test_dataset_pairs.py: verifies filename pairing and split validity
test_dataloader.py: verifies returned keys, tensor shapes, and normalization range
test_diffusion.py: verifies diffusion shape consistency and timestep behavior
test_unet_forward.py: verifies baseline model input/output compatibility
test_residual_forward.py: verifies residual model input/output compatibility
test_training_step.py: verifies one optimization step and finite loss
test_metrics.py: verifies PSNR, SSIM, Delta E, entropy, and optional NIQE functions
```

Recommended command:

```bash
pytest tests
```

## Evaluation Metrics

Core metrics:

```text
PSNR: higher is better
SSIM: higher is better
MSE/MAE: lower is better
Delta E: lower is better; the implemented version is CIE76 unless changed later
Entropy: supporting indicator only, because noise can also increase entropy
NIQE: supporting indicator only, optional depending on dependency stability
```

Final table format:

```text
Method              PSNR up   SSIM up   Delta E down   Entropy   NIQE
Turbid input         ...      ...       ...            ...          ...
Baseline U-Net       ...      ...       ...            ...          ...
Residual backbone    ...      ...       ...            ...          ...
```

## Training Plan

Local RTX 3050 training should be used only for debugging because 4 GB VRAM is limited.

Local debug settings:

```text
image size: 64 or 128
batch size: 1 or 2
subset size: 32 to 64 pairs
epochs: 1 to 5
```

Colab/A100 training settings:

```text
image size: 256
batch size: tune based on memory
epochs: start with 50, extend if validation improves
diffusion timesteps: 300 to 1000
sampling steps: 50 to 100
optimizer: AdamW
loss: MSE noise prediction loss
```

## Immediate Next Steps

1. Prepare Google Drive dataset/checkpoint/log/result folders.
2. Add full training scripts for baseline and residual models.
3. Add an evaluation script that loads checkpoints and writes final metrics/results.
4. Add a Colab notebook that mounts Drive, clones the repository, verifies paths, trains models, and saves outputs to Drive.
5. Run longer baseline and residual training on Colab/A100 if available.
