# Final Submission Checklist

Use this checklist before uploading/submitting the project.

## Required Items

- GitHub repository: `https://github.com/bedirhanozturk1/Underwater_Resnet_Restoration.git`
- Local final Word report: `../final_deliverables/final_report_150210321.docx`
- Local final report PDF: `../final_deliverables/final_report_150210321.pdf`
- Final grouped experiment summary: `../metric_summary_mean_std.csv`
- Supervisor checkpoint Word documents: `docs/supervisor_checkpoints/checkpoint_*.docx`
- Supervisor checkpoint PDF exports: `docs/supervisor_checkpoints/checkpoint_*.pdf`
- Colab workflow notebook: `notebooks/colab_training.ipynb`
- Training/evaluation/inference scripts: `scripts/`
- Main implementation code: `src/`
- Tests: `tests/`
- Local final presentation outline: `../final_deliverables/final_presentation_outline.md`
- Local final editable presentation: `../final_deliverables/final_presentation_150210321.pptx`
- Local final presentation PDF: `../final_deliverables/final_presentation_150210321.pdf`
- Local final submission notes: `../final_deliverables/README_FINAL_SUBMISSION.md`

## Result Files To Keep With The Report

- `report_outputs/metric_summary.csv`
- `report_outputs/training_loss_curves.png`
- `report_outputs/mse_comparison.png`
- `report_outputs/psnr_comparison.png`
- `report_outputs/ssim_comparison.png`
- `report_outputs/delta_e_cie76_comparison.png`
- `colab_results/residual_full/residual_comparison_grid.png`
- `colab_results/param_matched_unet/results/baseline_full/baseline_comparison_grid.png`

## Final Claim To Use

The safest final claim is:

```text
Across the grouped three-seed evaluation, the parameter-matched U-Net leads mean MSE, MAE, and PSNR, while the residual backbone leads mean SSIM and Delta E. Entropy is descriptive only and is not used as restoration-quality evidence.
```

## Claims To Avoid

- Do not claim state-of-the-art performance.
- Do not claim the residual model is best on every metric.
- Do not report quantitative metrics on unpaired/video datasets.
- Do not imply full video restoration, because the implemented model restores single frames/images.

## If Asked By The Supervisor

Question: Why did you run a parameter-matched U-Net?

Answer: To check whether the residual model improvement came only from having more parameters. The result shows that the matched U-Net leads mean pixel metrics, while the residual model leads mean SSIM and Delta E.

Question: What is the main contribution?

Answer: A leakage-controlled, capacity-aware comparison of diffusion denoising backbones for underwater restoration across three training seeds.

Question: Why are external datasets qualitative only?

Answer: They do not provide paired clear references, so full-reference metrics such as MSE, PSNR, SSIM, and Delta E would not be valid.
