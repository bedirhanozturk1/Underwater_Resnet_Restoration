from __future__ import annotations

import csv
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from pptx import Presentation
from pptx.util import Inches as PptInches
from pptx.util import Pt as PptPt


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = REPO_ROOT.parent
REPORT_MD = REPO_ROOT / "docs" / "final_report.md"
REPORT_OUTPUTS = PROJECT_ROOT / "report_outputs"
COLAB_RESULTS = PROJECT_ROOT / "colab_results"
DELIVERABLES = PROJECT_ROOT / "final_deliverables"


FIGURES = [
    (REPORT_OUTPUTS / "training_loss_curves.png", "Training and validation loss curves."),
    (REPORT_OUTPUTS / "mse_comparison.png", "MSE comparison across experiments."),
    (REPORT_OUTPUTS / "psnr_comparison.png", "PSNR comparison across experiments."),
    (REPORT_OUTPUTS / "ssim_comparison.png", "SSIM comparison across experiments."),
    (REPORT_OUTPUTS / "delta_e_cie76_comparison.png", "CIE76 Delta E comparison across experiments."),
    (COLAB_RESULTS / "residual_full" / "residual_comparison_grid.png", "Residual model qualitative test-set examples."),
    (
        COLAB_RESULTS
        / "param_matched_unet"
        / "results"
        / "baseline_full"
        / "baseline_comparison_grid.png",
        "Parameter-matched U-Net qualitative test-set examples.",
    ),
]


def main() -> None:
    DELIVERABLES.mkdir(parents=True, exist_ok=True)
    create_docx_report()
    create_presentation_outline()
    create_presentation_pptx()
    create_submission_readme()
    print(f"Final deliverables written to: {DELIVERABLES}")


def create_docx_report() -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(11)

    add_title_page(doc)
    add_markdown_body(doc, REPORT_MD.read_text(encoding="utf-8"))
    add_figures(doc)
    doc.save(DELIVERABLES / "final_report_150210321.docx")


def add_title_page(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Enhancing Diffusion-Based Underwater Image Restoration\nwith Residual Networks")
    run.bold = True
    run.font.size = Pt(20)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("\nFinal Project Report\n\nStudent ID: 150210321\n\n")
    p.add_run("GitHub: https://github.com/bedirhanozturk1/Underwater_Resnet_Restoration")
    doc.add_page_break()


def add_markdown_body(doc: Document, text: str) -> None:
    lines = text.splitlines()
    in_code = False
    table_block: list[str] = []

    def flush_table() -> None:
        nonlocal table_block
        if table_block:
            add_markdown_table(doc, table_block)
            table_block = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            flush_table()
            in_code = not in_code
            continue
        if in_code:
            add_paragraph(doc, line, style="Intense Quote")
            continue
        if line.startswith("|") and line.endswith("|"):
            table_block.append(line)
            continue
        flush_table()
        if not line:
            continue
        if line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=1)
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=2)
        elif line.startswith("- "):
            add_paragraph(doc, line[2:], style="List Bullet")
        else:
            add_paragraph(doc, strip_markdown_inline(line))


def add_markdown_table(doc: Document, lines: list[str]) -> None:
    rows = []
    for line in lines:
        cells = [strip_markdown_inline(cell.strip()) for cell in line.strip("|").split("|")]
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return
    max_cols = max(len(row) for row in rows)
    table = doc.add_table(rows=len(rows), cols=max_cols)
    table.style = "Table Grid"
    for r, row in enumerate(rows):
        for c in range(max_cols):
            cell = table.cell(r, c)
            cell.text = row[c] if c < len(row) else ""
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(8 if max_cols > 4 else 10)
                    if r == 0:
                        run.bold = True
    doc.add_paragraph()


def add_figures(doc: Document) -> None:
    doc.add_heading("Appendix: Figures", level=1)
    for figure_path, caption in FIGURES:
        if not figure_path.exists():
            add_paragraph(doc, f"Missing figure: {figure_path}")
            continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(figure_path), width=Inches(5.8))
        cap = doc.add_paragraph(caption)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_paragraph(doc: Document, text: str, style: str = "Normal") -> None:
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after = Pt(3)
    p.add_run(text)


def strip_markdown_inline(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    return text


def create_presentation_outline() -> None:
    summary_path = REPORT_OUTPUTS / "metric_summary.csv"
    rows = list(csv.DictReader(summary_path.open(encoding="utf-8"))) if summary_path.exists() else []
    residual = next((row for row in rows if row["experiment"] == "residual_128_50"), None)
    baseline = next((row for row in rows if row["experiment"] == "baseline_128_50"), None)
    param = next((row for row in rows if row["experiment"] == "param_matched_unet_128_50"), None)

    text = [
        "# Final Presentation Outline",
        "",
        "## Slide 1 - Title",
        "Enhancing Diffusion-Based Underwater Image Restoration with Residual Networks.",
        "",
        "## Slide 2 - Problem",
        "Underwater turbidity causes scattering, color distortion, and low contrast. The task is paired restoration from turbid image to clear/reference image.",
        "",
        "## Slide 3 - Dataset",
        "3672 paired images: 2937 train, 367 validation, 368 test. External/unpaired datasets are qualitative only.",
        "",
        "## Slide 4 - Method",
        "Conditional diffusion model with same noising objective. Baseline uses U-Net denoiser; proposed model uses ResNet-style residual denoiser.",
        "",
        "## Slide 5 - Fair Comparison",
        "Same split, preprocessing, diffusion schedule, loss, metrics, and test set for all quantitative experiments.",
        "",
        "## Slide 6 - Main Result",
    ]
    if baseline and residual:
        text.append(
            f"Baseline SSIM {baseline['ssim']} vs residual SSIM {residual['ssim']}; "
            f"baseline Delta E {baseline['delta_e_cie76']} vs residual Delta E {residual['delta_e_cie76']}."
        )
    text.extend(
        [
            "",
            "## Slide 7 - Capacity Control",
        ]
    )
    if param and residual:
        text.append(
            f"Parameter-matched U-Net improves MSE/PSNR ({param['mse']}, {param['psnr']}), "
            f"while residual remains better on SSIM/Delta E/Entropy ({residual['ssim']}, {residual['delta_e_cie76']}, {residual['entropy']})."
        )
    text.extend(
        [
            "",
            "## Slide 8 - Ablations",
            "Show 50 vs 100 epochs and 128 vs 256 resolution. Emphasize that longer training/resolution alone did not solve all metrics.",
            "",
            "## Slide 9 - Qualitative Results",
            "Show residual comparison grid and external inference examples. State clearly that external data has no paired reference.",
            "",
            "## Slide 10 - Conclusion",
            "Residual denoising improves structural/color-oriented restoration compared with the default baseline. Capacity matching shows pixel-wise metrics also depend on model size.",
        ]
    )
    (DELIVERABLES / "final_presentation_outline.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def create_presentation_pptx() -> None:
    prs = Presentation()
    prs.slide_width = PptInches(13.333)
    prs.slide_height = PptInches(7.5)

    add_slide(
        prs,
        "Enhancing Diffusion-Based Underwater Image Restoration",
        ["Residual denoising backbones inside conditional diffusion", "Student ID: 150210321"],
    )
    add_slide(
        prs,
        "Problem",
        [
            "Underwater turbidity causes scattering, low contrast, and color distortion.",
            "Task: restore turbid underwater image patches to paired clear/reference patches.",
            "Research question: does a residual denoising backbone improve the diffusion restoration model?",
        ],
    )
    add_slide(
        prs,
        "Dataset And Protocol",
        [
            "3672 paired clear/turbid underwater image pairs.",
            "Fixed split: 2937 train, 367 validation, 368 test.",
            "External unpaired/video datasets are qualitative only.",
            "All quantitative experiments use the same split, schedule, loss, and metrics.",
        ],
    )
    add_slide(
        prs,
        "Method",
        [
            "Conditional diffusion model predicts noise added to the clean target image.",
            "Baseline: conditional U-Net denoising backbone.",
            "Proposed: ResNet-style residual denoising backbone.",
            "Capacity control: larger U-Net with base_channels=42.",
        ],
    )
    add_picture_slide(prs, "Training Curves", REPORT_OUTPUTS / "training_loss_curves.png")
    add_slide(
        prs,
        "Main Quantitative Result",
        [
            "Default U-Net 128/50: SSIM 0.610758, Delta E 29.645203.",
            "Residual 128/50: SSIM 0.788963, Delta E 26.840257.",
            "Residual improves SSIM by 29.18% and reduces Delta E by 9.46% over the default baseline.",
        ],
    )
    add_picture_slide(prs, "SSIM Comparison", REPORT_OUTPUTS / "ssim_comparison.png")
    add_slide(
        prs,
        "Capacity-Control Result",
        [
            "Parameter-matched U-Net has the best MSE, MAE, and PSNR.",
            "Residual remains best on SSIM, Delta E, and entropy.",
            "Interpretation: capacity helps pixel-wise reconstruction; residual design helps structural/color-oriented behavior.",
        ],
    )
    add_picture_slide(prs, "Residual Qualitative Examples", COLAB_RESULTS / "residual_full" / "residual_comparison_grid.png")
    add_slide(
        prs,
        "Conclusion",
        [
            "Residual backbone clearly improves over the default U-Net baseline.",
            "The parameter-matched ablation prevents overclaiming and strengthens the analysis.",
            "Final claim: residual diffusion improves structural similarity, color difference, and output smoothness, but not every pixel-wise metric.",
        ],
    )
    prs.save(DELIVERABLES / "final_presentation_150210321.pptx")


def add_slide(prs: Presentation, title: str, bullets: list[str]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = title
    body = slide.placeholders[1].text_frame
    body.clear()
    for index, bullet in enumerate(bullets):
        paragraph = body.paragraphs[0] if index == 0 else body.add_paragraph()
        paragraph.text = bullet
        paragraph.level = 0
        paragraph.font.size = PptPt(24)


def add_picture_slide(prs: Presentation, title: str, image_path: Path) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title
    if image_path.exists():
        slide.shapes.add_picture(str(image_path), PptInches(1.0), PptInches(1.25), width=PptInches(11.3))
    else:
        box = slide.shapes.add_textbox(PptInches(1.0), PptInches(2.5), PptInches(11.0), PptInches(1.0))
        box.text_frame.text = f"Missing image: {image_path}"


def create_submission_readme() -> None:
    text = """# Final Submission Notes

This folder contains final local deliverables generated from the repository and completed experiment outputs.

## Files

- `final_report_150210321.docx`: Word final report generated from `docs/final_report.md`.
- `final_report_150210321.pdf`: PDF export of the final report, if generated through Word.
- `final_presentation_outline.md`: concise slide-by-slide presentation outline.
- `final_presentation_150210321.pptx`: editable presentation file.
- `final_presentation_150210321.pdf`: PDF export of the presentation, if generated through PowerPoint.
- `README_FINAL_SUBMISSION.md`: this file.

## GitHub

Repository: https://github.com/bedirhanozturk1/Underwater_Resnet_Restoration

Latest code includes training, evaluation, inference, Colab workflow, final experiment summaries, and supervisor checkpoint documents.

## Results Location

The quantitative summary and plots are in `report_outputs/` at the project root. Colab result grids and raw metric CSV files are in `colab_results/`.

## Important Reporting Note

Use the capacity-control interpretation. The residual backbone is not best on every metric after parameter matching. It is strongest on SSIM, Delta E, and entropy, while the parameter-matched U-Net is slightly stronger on MSE, MAE, and PSNR.
"""
    (DELIVERABLES / "README_FINAL_SUBMISSION.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
