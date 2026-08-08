# Enhancing Diffusion-Based Underwater Image Restoration with Residual Networks

> **Superseded draft:** This Markdown report contains results from the original filename-random split. A later audit found source-chart overlap and exact-pair duplicates across partitions. Do not submit or cite its quantitative claims. It will be regenerated after the grouped three-model, three-seed experiment matrix completes.

Student ID: 150210321

## Abstract

Underwater images often suffer from turbidity, scattering, low contrast, and color distortion. These degradations reduce visual quality and make downstream analysis difficult. This project investigates a supervised diffusion-based restoration pipeline for transforming turbid underwater image patches into clearer reference patches. The baseline model uses a conditional U-Net denoising backbone, while the proposed model replaces this backbone with a ResNet-style residual denoising network under the same diffusion training objective.

The experiments use 3672 paired clear/turbid underwater color-patch images, split into 2937 training, 367 validation, and 368 test images. The evaluation uses MSE, MAE, PSNR, SSIM, CIE76 Delta E, and entropy. The residual backbone clearly improves over the default U-Net baseline at the same 128x128, 50-epoch setting, especially in SSIM and color-difference metrics. A parameter-matched U-Net ablation shows that increasing U-Net capacity can improve pixel-wise metrics, while the residual model remains stronger on SSIM, Delta E, and entropy. The final conclusion is that residual denoising backbones improve structural and color-oriented restoration behavior in this diffusion setting, although they do not dominate every pixel-wise metric.

## 1. Introduction

Underwater image restoration is challenging because light attenuation, suspended particles, scattering, and non-uniform illumination produce strong visual degradation. Restoring these images is useful for marine inspection, underwater robotics, monitoring systems, and visual documentation. Traditional enhancement methods often improve contrast or color globally, but they may not learn the paired mapping between degraded and clear observations.

Diffusion models have recently become a strong generative modeling approach because they learn to reverse a gradual noising process. For image restoration, a conditional diffusion model can use the degraded image as conditioning information and learn to predict the noise added to the clear target image. The quality of this denoising prediction depends heavily on the neural backbone used inside the diffusion process.

This project studies whether replacing a standard conditional U-Net denoising backbone with a ResNet-style residual backbone improves underwater image restoration. The core comparison is controlled: both models use the same dataset, same split, same preprocessing, same diffusion noise schedule, same optimization setup, and same evaluation metrics.

## 2. Problem Definition

The task is supervised paired image restoration:

```text
turbid underwater image -> restored clear/reference image
```

For each training pair, the input is a turbid underwater image patch and the target is the corresponding clear/reference patch. The diffusion model is trained to denoise the clear target while conditioned on the turbid input.

The main research question is:

```text
Does a ResNet-style residual denoising backbone improve conditional diffusion-based underwater image restoration compared with a standard U-Net denoising backbone?
```

## 3. Dataset

The supervised training data consists of 3672 matched clear/turbid underwater image pairs. The filenames were checked so that every turbid image has a corresponding clear reference image. The split is fixed and reused across all experiments:

| Split | Image Pairs |
|---|---:|
| Training | 2937 |
| Validation | 367 |
| Test | 368 |

The paired dataset is the only dataset used for supervised training and quantitative evaluation. Additional unpaired image/video-derived datasets are used only for qualitative inference because they do not provide paired clear references. This separation prevents unfair quantitative claims on unpaired data.

## 4. Methodology

### 4.1 Conditional Diffusion Formulation

The model follows a denoising diffusion objective. During training, Gaussian noise is added to the clean target image at a randomly sampled timestep. The neural network receives the noisy target, the timestep, and the turbid conditioning image, then predicts the added noise. The loss is the noise-prediction error.

The same diffusion formulation is used for all backbone comparisons. Therefore, the comparison focuses on the denoising architecture rather than changes in the objective.

### 4.2 Baseline U-Net Backbone

The baseline uses a conditional U-Net denoising backbone. The turbid image and noisy target are concatenated as input channels, and timestep embeddings are injected into the network. The U-Net structure captures multi-scale information through encoder-decoder paths and skip connections.

### 4.3 Proposed Residual Backbone

The proposed model replaces the standard backbone with a ResNet-style residual denoising backbone. Residual blocks make the network learn refinements through skip-connected transformations, which can improve gradient flow and preserve useful low-level structure. This is relevant for underwater restoration because structural edges and color consistency can be degraded by scattering and turbidity.

### 4.4 Fair Comparison Protocol

All main experiments use the same:

- paired dataset
- train/validation/test split
- preprocessing and image normalization
- diffusion noise schedule
- training loss
- test set
- evaluation metrics

This protocol makes the U-Net and residual-backbone results directly comparable.

## 5. Implementation

The implementation is organized as a reproducible Python/PyTorch project. The main components are:

| Component | Path |
|---|---|
| Training script | `scripts/train_model.py` |
| Evaluation script | `scripts/evaluate_model.py` |
| Inference script | `scripts/run_inference.py` |
| Model factory | `src/models/factory.py` |
| Diffusion/sampling logic | `src/models/sampling.py` |
| Colab workflow | `notebooks/colab_training.ipynb` |
| Final result summary | `docs/final_results_summary.md` |

Training was performed on Google Colab using an A100 GPU. Checkpoints, logs, and generated outputs were kept outside GitHub in the project Drive/results folders to avoid committing large artifacts.

## 6. Experiments

The final experiment set includes the main model comparison and several ablations:

| Experiment | Model | Image Size | Epochs | Purpose |
|---|---|---:|---:|---|
| Main baseline | Conditional U-Net | 128 | 50 | Standard diffusion denoising backbone |
| Main proposed | ResNet-style residual backbone | 128 | 50 | Proposed residual denoising backbone |
| Capacity control | Parameter-matched U-Net | 128 | 50 | Check whether gains come only from parameter count |
| Extended training | U-Net and residual | 128 | 100 | Check longer training behavior |
| Resolution ablation | U-Net and residual | 256 | 50 | Check higher-resolution behavior |
| Qualitative generalization | Residual | 128 | inference only | Test external unpaired/video-derived inputs qualitatively |

The parameter-matched U-Net uses `base_channels=42`, resulting in approximately 901,797 parameters, close to the residual model with approximately 886,371 parameters. This is an important control experiment because it tests whether improvements are caused only by model capacity.

## 7. Quantitative Results

All quantitative metrics are computed on the 368-image paired test split.

| Experiment | MSE | MAE | PSNR | SSIM | Delta E | Entropy |
|---|---:|---:|---:|---:|---:|---:|
| Baseline U-Net, 128, 50 epoch | 0.039444 | 0.168026 | 15.681501 | 0.610758 | 29.645203 | 5.095362 |
| Parameter-matched U-Net, 128, 50 epoch | 0.034294 | 0.155805 | 16.356273 | 0.746291 | 27.225774 | 4.790907 |
| Residual backbone, 128, 50 epoch | 0.035727 | 0.159895 | 16.304393 | 0.788963 | 26.840257 | 4.368050 |
| Baseline U-Net, 128, 100 epoch | 0.037111 | 0.163163 | 15.976561 | 0.623376 | 28.571008 | 4.943213 |
| Residual backbone, 128, 100 epoch | 0.035936 | 0.160301 | 16.352538 | 0.785447 | 26.866293 | 4.710935 |
| Baseline U-Net, 256, 50 epoch | 0.039126 | 0.167594 | 15.749889 | 0.609380 | 29.117468 | 4.873310 |
| Residual backbone, 256, 50 epoch | 0.039173 | 0.168835 | 15.900427 | 0.807967 | 27.078848 | 4.667301 |

Compared with the default 128x128 50-epoch U-Net baseline, the residual model improves the main metrics as follows:

| Metric | Baseline | Residual | Change |
|---|---:|---:|---:|
| MSE | 0.039444 | 0.035727 | 9.42% lower |
| MAE | 0.168026 | 0.159895 | 4.84% lower |
| PSNR | 15.681501 | 16.304393 | +0.622892 dB |
| SSIM | 0.610758 | 0.788963 | 29.18% higher |
| Delta E | 29.645203 | 26.840257 | 9.46% lower |
| Entropy | 5.095362 | 4.368050 | 14.27% lower |

The parameter-matched U-Net ablation changes the interpretation. The larger U-Net is slightly better than the residual model on MSE, MAE, and PSNR. However, the residual model remains better on SSIM, Delta E, and entropy:

| Metric | Parameter-Matched U-Net | Residual | Interpretation |
|---|---:|---:|---|
| MSE | 0.034294 | 0.035727 | U-Net capacity gives lower pixel error |
| MAE | 0.155805 | 0.159895 | U-Net capacity gives lower absolute error |
| PSNR | 16.356273 | 16.304393 | U-Net capacity is slightly higher |
| SSIM | 0.746291 | 0.788963 | Residual gives stronger structure |
| Delta E | 27.225774 | 26.840257 | Residual gives lower color difference |
| Entropy | 4.790907 | 4.368050 | Residual gives smoother/lower-noise outputs |

## 8. Discussion

The main result supports the usefulness of residual denoising backbones in this underwater diffusion restoration setting. The residual model is much stronger than the standard U-Net baseline in SSIM and Delta E, which are important for structural and color-oriented restoration quality.

The capacity-control experiment prevents overclaiming. It shows that increasing U-Net capacity can improve pixel-wise reconstruction metrics. Therefore, the final conclusion should not claim that the residual model is universally best across every metric. A more accurate conclusion is that residual architecture improves structural consistency, color-difference behavior, and output smoothness, while model capacity can improve direct pixel-wise measures such as MSE and PSNR.

The 100-epoch experiment shows that longer training improves the baseline but does not consistently improve the residual model. This suggests that the residual model reaches its effective performance earlier under the current hyperparameters, or that it needs different learning-rate or regularization tuning for longer schedules. The 256-resolution experiment improves residual SSIM but does not improve every pixel-wise metric, so resolution alone is not sufficient without additional tuning.

## 9. Qualitative Generalization

The trained residual model was also applied to auxiliary unpaired turbid images and video-derived frames. These outputs are qualitative only because no paired clear references are available. The qualitative results are useful to inspect whether the model can produce plausible restoration behavior outside the paired test set, but they should not be used for quantitative claims.

The qualitative inference results show that the model can reduce some turbidity and produce smoother outputs, but generalization is limited by the training distribution. Since the main paired dataset consists of color-patch images, the model is best matched to patch-like underwater inputs and may not fully generalize to complex natural underwater scenes.

## 10. Limitations

- The supervised training set contains paired color-patch images, so generalization to full natural underwater scenes is limited.
- External datasets are unpaired, so they are used only for qualitative inference.
- The model restores single images and does not implement temporal consistency for video restoration.
- The residual backbone improves structural/color metrics but does not dominate all pixel-wise metrics after parameter matching.
- Further hyperparameter tuning may be needed for longer training and higher-resolution restoration.

## 11. Conclusion

This project implemented and evaluated a conditional diffusion-based underwater image restoration pipeline with two denoising backbones: a standard U-Net baseline and a ResNet-style residual backbone. The residual backbone significantly improves over the default U-Net baseline on the paired test set, especially in SSIM and Delta E. A parameter-matched U-Net ablation shows that some pixel-wise improvements can also be achieved by increasing U-Net capacity, but the residual model remains stronger on structural similarity, color difference, and entropy.

The final contribution is therefore a controlled architectural study showing that residual denoising backbones are beneficial for structural and color-oriented underwater restoration within a diffusion framework, while also documenting the role of parameter count through a capacity-control ablation.

## 12. Future Work

- Train on larger and more diverse paired underwater datasets.
- Tune longer training schedules and learning-rate decay for the residual model.
- Explore stronger diffusion samplers and perceptual losses.
- Add temporal consistency for video-based underwater restoration.
- Compare against non-diffusion restoration baselines such as direct U-Net regression or GAN-based enhancement.

## References

[1] J. Ho, A. Jain, and P. Abbeel, "Denoising Diffusion Probabilistic Models," NeurIPS, 2020.

[2] O. Ronneberger, P. Fischer, and T. Brox, "U-Net: Convolutional Networks for Biomedical Image Segmentation," MICCAI, 2015.

[3] K. He, X. Zhang, S. Ren, and J. Sun, "Deep Residual Learning for Image Recognition," CVPR, 2016.

[4] C. Li, C. Guo, W. Ren, R. Cong, J. Hou, S. Kwong, and D. Tao, "An Underwater Image Enhancement Benchmark Dataset and Beyond," IEEE Transactions on Image Processing, 2020.
