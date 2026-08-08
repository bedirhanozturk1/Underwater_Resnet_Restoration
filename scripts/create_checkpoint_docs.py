from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = REPO_ROOT.parent
REPORT_ASSETS = PROJECT_ROOT / "report_assets"
REPORT_OUTPUTS = PROJECT_ROOT / "report_outputs"
COLAB_RESULTS = PROJECT_ROOT / "colab_results"


CHECKPOINTS = [
    {
        "file": "checkpoint_01_dataset_setup.docx",
        "title": "Checkpoint 1: Dataset Setup",
        "objective": "Verify the paired underwater dataset and define the supervised restoration task.",
        "key_message": "The project has a clean paired dataset and a fixed split for fair training and testing.",
        "completed": [
            "Verified 3672 matched clear/turbid image pairs.",
            "Created fixed train, validation, and test split files.",
            "Separated paired training data from unpaired qualitative data.",
        ],
        "table": [["Split", "Pairs"], ["Train", "2937"], ["Validation", "367"], ["Test", "368"]],
        "figures": [
            (REPORT_ASSETS / "paired_underwater_patches.png", "Example verified paired image patch."),
            (REPORT_ASSETS / "candidate_pair_sheet.png", "Dataset pairing examples used during inspection."),
        ],
        "notes": ["Quantitative metrics are valid only on paired clear/turbid data."],
    },
    {
        "file": "checkpoint_02_diffusion_pipeline.docx",
        "title": "Checkpoint 2: DataLoader and Diffusion Pipeline",
        "objective": "Show that paired images enter the model correctly and that the diffusion training task is implemented.",
        "key_message": "The data pipeline, noising process, and tests are ready before full model training.",
        "completed": [
            "Implemented normalized paired image loading.",
            "Implemented timestep sampling and linear beta schedule.",
            "Added sanity tests for dataset pairing, diffusion, and training steps.",
        ],
        "table": [["Component", "Status"], ["Paired DataLoader", "Completed"], ["Forward diffusion", "Completed"], ["Unit tests", "Passing"]],
        "figures": [(REPORT_ASSETS / "proposed_pipeline.png", "Conditional diffusion restoration pipeline.")],
        "notes": ["The same diffusion objective is used for both baseline and residual models."],
    },
    {
        "file": "checkpoint_03_baseline_unet.docx",
        "title": "Checkpoint 3: Baseline U-Net Diffusion Model",
        "objective": "Train and evaluate the baseline conditional U-Net denoising backbone.",
        "key_message": "The baseline model gives the reference point for all later comparisons.",
        "completed": [
            "Implemented conditional U-Net with timestep conditioning.",
            "Completed baseline training and evaluation on the fixed test split.",
            "Generated metric CSV files and qualitative comparison grids.",
        ],
        "table": [["Metric", "Baseline 128/50"], ["MSE", "0.039444"], ["PSNR", "15.681501"], ["SSIM", "0.610758"], ["Delta E", "29.645203"]],
        "figures": [(COLAB_RESULTS / "baseline_full" / "baseline_comparison_grid.png", "Baseline qualitative test examples.")],
        "notes": ["This model is the default U-Net diffusion baseline, not the proposed contribution."],
    },
    {
        "file": "checkpoint_04_residual_backbone.docx",
        "title": "Checkpoint 4: Residual Denoising Backbone",
        "objective": "Replace the U-Net denoising backbone with a ResNet-style residual backbone under the same diffusion task.",
        "key_message": "The proposed residual backbone improves structural and color-oriented metrics over the default baseline.",
        "completed": [
            "Implemented residual blocks and residual denoising backbone.",
            "Trained the residual model using the same paired split and objective.",
            "Compared residual and baseline outputs on the same 368 test images.",
        ],
        "table": [["Metric", "U-Net 128/50", "Residual 128/50"], ["MSE", "0.039444", "0.035727"], ["PSNR", "15.681501", "16.304393"], ["SSIM", "0.610758", "0.788963"], ["Delta E", "29.645203", "26.840257"]],
        "figures": [(COLAB_RESULTS / "residual_full" / "residual_comparison_grid.png", "Residual qualitative test examples."), (REPORT_OUTPUTS / "ssim_comparison.png", "SSIM comparison across experiments.")],
        "notes": ["Residual improves default-baseline SSIM by 29.18% and reduces Delta E by 9.46%."],
    },
    {
        "file": "checkpoint_05_full_results.docx",
        "title": "Checkpoint 5: Full Results",
        "objective": "Evaluate main models and ablations on the fixed 368-image test split.",
        "key_message": "The complete result table is ready and uses the same test split for every quantitative claim.",
        "completed": [
            "Evaluated 128x128 50-epoch baseline and residual models.",
            "Evaluated 100-epoch training variants.",
            "Evaluated 256x256 resolution variants.",
            "Generated final metric summary and plots.",
        ],
        "table": [["Experiment", "PSNR", "SSIM", "Delta E"], ["U-Net 128/50", "15.681501", "0.610758", "29.645203"], ["Residual 128/50", "16.304393", "0.788963", "26.840257"], ["U-Net 128/100", "15.976561", "0.623376", "28.571008"], ["Residual 128/100", "16.352538", "0.785447", "26.866293"], ["Residual 256/50", "15.900427", "0.807967", "27.078848"]],
        "figures": [(REPORT_OUTPUTS / "training_loss_curves.png", "Training and validation loss curves."), (REPORT_OUTPUTS / "delta_e_cie76_comparison.png", "Delta E comparison across experiments.")],
        "notes": ["Longer training helps the baseline but does not make it structurally stronger than the residual model."],
    },
    {
        "file": "checkpoint_06_ablation_generalization.docx",
        "title": "Checkpoint 6: Capacity Control and Generalization",
        "objective": "Check parameter-count effects and evaluate qualitative behavior on unpaired external inputs.",
        "key_message": "The capacity-control result makes the final claim honest: residual is not best on every metric, but remains best on SSIM, Delta E, and entropy.",
        "completed": [
            "Completed parameter-matched U-Net capacity control with base_channels=42.",
            "Compared parameter-matched U-Net with the residual model.",
            "Ran qualitative inference on unpaired turbid images and video-derived frames.",
        ],
        "table": [["Metric", "Matched U-Net", "Residual", "Better"], ["MSE", "0.034294", "0.035727", "Matched U-Net"], ["PSNR", "16.356273", "16.304393", "Matched U-Net"], ["SSIM", "0.746291", "0.788963", "Residual"], ["Delta E", "27.225774", "26.840257", "Residual"], ["Entropy", "4.790907", "4.368050", "Residual"]],
        "figures": [(COLAB_RESULTS / "param_matched_unet" / "results" / "baseline_full" / "baseline_comparison_grid.png", "Parameter-matched U-Net examples."), (REPORT_OUTPUTS / "mse_comparison.png", "MSE comparison showing the capacity-control effect.")],
        "notes": ["External datasets are qualitative only because paired clear references are not available."],
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create richer supervisor checkpoint DOCX files.")
    parser.add_argument("--output-dir", type=Path, default=Path("docs/supervisor_checkpoints"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for checkpoint in CHECKPOINTS:
        write_docx(checkpoint, args.output_dir / checkpoint["file"])
    print(f"Wrote {len(CHECKPOINTS)} checkpoint documents to {args.output_dir}")


def write_docx(checkpoint: dict[str, object], output_path: Path) -> None:
    doc = Document()
    setup(doc)
    title(doc, str(checkpoint["title"]))
    section(doc, "Objective")
    para(doc, str(checkpoint["objective"]))
    section(doc, "Key Message")
    callout(doc, str(checkpoint["key_message"]))
    section(doc, "Completed Work")
    for item in checkpoint["completed"]:  # type: ignore[index]
        bullet(doc, str(item))
    section(doc, "Evidence")
    add_table(doc, checkpoint["table"])  # type: ignore[arg-type]
    for path, text in checkpoint["figures"]:  # type: ignore[index]
        add_picture(doc, Path(path), str(text))
    section(doc, "Notes")
    for item in checkpoint["notes"]:  # type: ignore[index]
        bullet(doc, str(item))
    doc.save(output_path)


def setup(doc: Document) -> None:
    section_obj = doc.sections[0]
    section_obj.top_margin = Inches(0.65)
    section_obj.bottom_margin = Inches(0.65)
    section_obj.left_margin = Inches(0.75)
    section_obj.right_margin = Inches(0.75)
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(10.5)


def title(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(31, 78, 121)


def section(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(12)


def para(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(3)
    p.add_run(text)


def bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(1)
    p.add_run(text)


def callout(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(5)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(11)


def add_table(doc: Document, rows: list[list[str]]) -> None:
    table = doc.add_table(rows=len(rows), cols=max(len(row) for row in rows))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(8.5)
                    if r == 0:
                        run.bold = True
                        run.font.color.rgb = RGBColor(31, 78, 121)
    doc.add_paragraph()


def add_picture(doc: Document, path: Path, text: str) -> None:
    if not path.exists():
        para(doc, f"Missing figure: {path}")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(1)
    p.add_run().add_picture(str(path), width=Inches(5.6))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(5)
    run = cap.add_run(text)
    run.italic = True
    run.font.size = Pt(8.5)


if __name__ == "__main__":
    main()
