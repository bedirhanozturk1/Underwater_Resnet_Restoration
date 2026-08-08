from __future__ import annotations

import csv
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from pptx import Presentation
from pptx.util import Inches as PptInches
from pptx.util import Pt as PptPt


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = REPO_ROOT.parent
REPORT_OUTPUTS = PROJECT_ROOT / "report_outputs"
REPORT_ASSETS = PROJECT_ROOT / "report_assets"
COLAB_RESULTS = PROJECT_ROOT / "colab_results"
DELIVERABLES = PROJECT_ROOT / "final_deliverables"
REPORT_TEMPLATE = PROJECT_ROOT / "myfriendsproject" / "04-4902-Project_Report_Template.docx"


def main() -> None:
    DELIVERABLES.mkdir(parents=True, exist_ok=True)
    create_docx_report()
    create_presentation_outline()
    create_presentation_pptx()
    create_submission_readme()
    print(f"Final deliverables written to: {DELIVERABLES}")


def create_docx_report() -> None:
    doc = Document(REPORT_TEMPLATE) if REPORT_TEMPLATE.exists() else Document()
    setup_document(doc)
    rebuild_template_cover_and_body(doc)
    output = DELIVERABLES / "final_report_150210321.docx"
    try:
        doc.save(output)
    except PermissionError:
        doc.save(DELIVERABLES / "final_report_150210321_template.docx")


def rebuild_template_cover_and_body(doc: Document) -> None:
    replace_template_cover(doc)
    replace_template_contents(doc)
    remove_template_body(doc)
    add_summary(doc)
    add_introduction(doc)
    add_background(doc)
    add_system_design(doc)
    add_implementation(doc)
    add_experiments(doc)
    add_results(doc)
    add_discussion(doc)
    add_conclusion(doc)
    add_references(doc)
    add_appendix(doc)


def setup_document(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(10.5)
    styles["Heading 1"].font.name = "Times New Roman"
    styles["Heading 1"].font.size = Pt(15)
    styles["Heading 1"].font.bold = True
    styles["Heading 2"].font.name = "Times New Roman"
    styles["Heading 2"].font.size = Pt(12)
    styles["Heading 2"].font.bold = True


def replace_template_cover(doc: Document) -> None:
    replacements = {
        "Artifical Intelligence & Data Engineering": "Artifical Intelligence & Data Engineering",
        "Design Project Report": "Design Project Report",
        "Title": "Title",
        "Building A Large Language Model Based Artificial General Intelligence (AGI) System": "Enhancing Diffusion-Based Underwater Image Restoration with Residual Networks",
        "Prepared By": "Prepared By",
        "15010000 Elon MUSK": "150210321 Bedirhan OZTURK",
        "15010001 Bill GATES": "",
        "Supervisor": "Supervisor",
        "Assoc. Prof. Dr. A. Cüneyd TANTUĞ": "Prof. Dr. Behcet Ugur Toreyin",
        "May, 2024": "August, 2026",
    }
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text in replacements:
            set_paragraph_text(paragraph, replacements[text], keep_style=True)


def replace_template_contents(doc: Document) -> None:
    replacements = {
        "1\tINTRODUCTION\t1": "1\tINTRODUCTION\t1",
        "2\tBACKGROUND\t2": "2\tBACKGROUND\t3",
        "3\tSYSTEM REQUIREMENTS\t3": "3\tSYSTEM DESIGN\t4",
        "3.1\tDesign Constraints and Relevant Engineering Standards\t3": "3.1\tTask Definition\t4",
        "3.2\tFunctional Requirements\t3": "3.2\tDataset Split\t4",
        "3.3\tNon-Functional Requirements\t3": "4\tIMPLEMENTATION\t5",
        "3.4\tEvaluation Criteria\t3": "5\tEXPERIMENTAL SETUP\t6",
        "4\tSYSTEM ARCHITECTURE\t4": "6\tRESULTS\t7",
        "5\tRESULTS AND EVALUATION\t5": "7\tDISCUSSION AND LIMITATIONS\t10",
        "6\tCONCLUSIONS AND FUTURE WORKS\t6": "8\tCONCLUSION\t11",
        "7\tREFERENCES\t7": "9\tREFERENCES\t12",
    }
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text in replacements:
            set_paragraph_text(paragraph, replacements[text], keep_style=True)
            first = replacements[text].split("\t", 1)[0]
            if "." in first:
                paragraph.style = "toc 2"
            else:
                paragraph.style = "toc 1"


def remove_template_body(doc: Document) -> None:
    start = None
    for index, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip() == "SUMMARY":
            start = index
            break
    if start is None:
        doc.add_page_break()
        return
    for paragraph in list(doc.paragraphs[start:]):
        element = paragraph._element
        element.getparent().remove(element)


def set_paragraph_text(paragraph, text: str, keep_style: bool = True) -> None:
    style = paragraph.style if keep_style else None
    alignment = paragraph.alignment
    paragraph.clear()
    if style is not None:
        paragraph.style = style
    paragraph.alignment = alignment
    if text:
        paragraph.add_run(text)


def add_summary(doc: Document) -> None:
    preamble_heading(doc, "SUMMARY")
    para(
        doc,
        "This project studies underwater image restoration with a conditional diffusion model. "
        "The input is a turbid underwater image patch and the target is its paired clear reference patch. "
        "The baseline uses a conditional U-Net denoising backbone. The proposed model replaces it with a "
        "ResNet-style residual denoising backbone while keeping the same diffusion objective.",
    )
    para(
        doc,
        "The supervised dataset contains 3672 paired clear/turbid image pairs. The fixed split is 2937 training, "
        "367 validation, and 368 test images. All quantitative experiments use the same test split and the same "
        "metrics: MSE, MAE, PSNR, SSIM, CIE76 Delta E, and entropy.",
    )
    add_picture(doc, REPORT_ASSETS / "paired_underwater_patches.png", 4.7)
    caption(doc, "Figure 1. Example paired turbid and clear underwater image patches used in the supervised task.")
    para(
        doc,
        "The residual backbone clearly improves over the default U-Net baseline. A capacity-control experiment with a "
        "parameter-matched U-Net shows that a larger U-Net improves pixel-wise metrics, while the residual model remains "
        "stronger on SSIM, Delta E, and entropy. Therefore, the final conclusion is deliberately conservative: residual "
        "backbones improve structural and color-oriented restoration behavior, but they are not best on every metric.",
    )
    doc.add_page_break()


def add_table_of_contents(doc: Document) -> None:
    preamble_heading(doc, "CONTENTS")
    rows = [
        ("1", "INTRODUCTION"),
        ("2", "BACKGROUND"),
        ("3", "SYSTEM DESIGN"),
        ("4", "IMPLEMENTATION"),
        ("5", "EXPERIMENTAL SETUP"),
        ("6", "RESULTS"),
        ("7", "DISCUSSION AND LIMITATIONS"),
        ("8", "CONCLUSION"),
        ("9", "REFERENCES"),
        ("10", "APPENDIX"),
    ]
    for number, title in rows:
        para(doc, f"{number}.\t{title}")
    doc.add_page_break()


def add_introduction(doc: Document) -> None:
    heading(doc, "INTRODUCTION")
    para(
        doc,
        "Underwater images are degraded by light absorption, scattering, turbidity, and color distortion. "
        "These degradations reduce contrast, hide details, and create strong blue-green color casts. "
        "Restoring underwater images is useful for marine inspection, robotics, monitoring, and visual documentation.",
    )
    para(
        doc,
        "Diffusion models are suitable for restoration because they learn a reverse denoising process. In a conditional "
        "restoration setting, the degraded image guides the model while it denoises the clean target image. The denoising "
        "backbone is therefore a key architectural component.",
    )
    para(
        doc,
        "This project compares two denoising backbones inside the same diffusion framework: a standard conditional U-Net "
        "and a ResNet-style residual backbone. The purpose is to test whether residual learning improves restoration "
        "quality under a controlled and reproducible protocol.",
    )
    add_picture(doc, REPORT_ASSETS / "proposed_pipeline.png", 6.0)
    caption(doc, "Figure 2. Overall comparison pipeline: same diffusion task, different denoising backbones.")


def add_background(doc: Document) -> None:
    heading(doc, "BACKGROUND")
    subheading(doc, "Underwater Image Degradation")
    para(
        doc,
        "Underwater degradation is not ordinary noise. Red wavelengths disappear faster, suspended particles scatter light, "
        "and turbidity reduces local contrast. This produces blurred edges, color shifts, and haze-like artifacts.",
    )
    subheading(doc, "U-Net And Residual Networks")
    para(
        doc,
        "U-Net is a strong image-to-image baseline because encoder-decoder processing and skip connections preserve spatial "
        "information. Residual networks add identity shortcuts and learn refinements, which can help preserve structure while "
        "correcting degradations.",
    )
    subheading(doc, "Diffusion Restoration")
    para(
        doc,
        "In denoising diffusion, noise is added to a target image during training and the network learns to predict that noise. "
        "For this project, the turbid image is used as conditioning information. The training objective is unchanged between "
        "the baseline and proposed model.",
    )


def add_system_design(doc: Document) -> None:
    heading(doc, "SYSTEM DESIGN")
    subheading(doc, "Task Definition")
    add_table(doc, [["Input", "Output", "Learning Type"], ["Turbid underwater patch", "Clear/reference patch", "Supervised paired restoration"]])
    para(doc, "The model learns the paired mapping from turbid input to clear reference image through diffusion denoising.")
    subheading(doc, "Dataset Split")
    add_table(doc, [["Split", "Image Pairs"], ["Training", "2937"], ["Validation", "367"], ["Test", "368"]])
    para(doc, "The split is fixed and reused for every quantitative result. External unpaired images are used only qualitatively.")
    add_picture(doc, REPORT_ASSETS / "candidate_pair_sheet.png", 5.8)
    caption(doc, "Figure 3. Candidate paired examples used during dataset verification.")


def add_implementation(doc: Document) -> None:
    heading(doc, "IMPLEMENTATION")
    para(doc, "The implementation is organized as a reproducible PyTorch project with separate scripts for training, evaluation, and inference.")
    add_table(
        doc,
        [
            ["Component", "Path"],
            ["Training", "scripts/train_model.py"],
            ["Evaluation", "scripts/evaluate_model.py"],
            ["Inference", "scripts/run_inference.py"],
            ["Model factory", "src/models/factory.py"],
            ["Sampling", "src/models/sampling.py"],
            ["Colab workflow", "notebooks/colab_training.ipynb"],
        ],
    )
    para(doc, "Full training was performed on Google Colab with A100 availability. Large datasets, logs, and checkpoints are kept outside GitHub.")


def add_experiments(doc: Document) -> None:
    heading(doc, "EXPERIMENTAL SETUP")
    add_table(
        doc,
        [
            ["Experiment", "Model", "Image Size", "Epochs", "Purpose"],
            ["Main baseline", "Conditional U-Net", "128", "50", "Default denoising backbone"],
            ["Main proposed", "Residual backbone", "128", "50", "Proposed backbone"],
            ["Capacity control", "Parameter-matched U-Net", "128", "50", "Check parameter-count effect"],
            ["Longer training", "U-Net / residual", "128", "100", "Training-duration ablation"],
            ["Resolution ablation", "U-Net / residual", "256", "50", "Resolution effect"],
            ["Generalization", "Residual", "128", "Inference", "Qualitative external data"],
        ],
        font_size=8,
    )
    para(
        doc,
        "The parameter-matched U-Net uses base_channels=42. It has about 901,797 parameters, close to the residual model "
        "with about 886,371 parameters. This experiment checks whether improvements come only from model size.",
    )


def add_results(doc: Document) -> None:
    heading(doc, "RESULTS")
    subheading(doc, "Full Test Metrics")
    add_metric_summary_table(doc)
    para(doc, "All numbers are computed on the same 368-image paired test split.")
    add_picture(doc, REPORT_OUTPUTS / "training_loss_curves.png", 5.8)
    caption(doc, "Figure 4. Training and validation loss curves for completed experiments.")
    add_picture(doc, REPORT_OUTPUTS / "ssim_comparison.png", 5.6)
    caption(doc, "Figure 5. SSIM comparison. Higher is better.")
    add_picture(doc, REPORT_OUTPUTS / "delta_e_cie76_comparison.png", 5.6)
    caption(doc, "Figure 6. CIE76 Delta E comparison. Lower is better.")

    subheading(doc, "Main Interpretation")
    para(
        doc,
        "At 128x128 and 50 epochs, the residual backbone improves over the default U-Net baseline. It lowers MSE by 9.42%, "
        "raises SSIM by 29.18%, and lowers Delta E by 9.46%. This supports the value of residual denoising blocks for "
        "structural and color-oriented underwater restoration.",
    )
    para(
        doc,
        "The parameter-matched U-Net ablation is important. The larger U-Net is slightly better on MSE, MAE, and PSNR. "
        "However, the residual model remains better on SSIM, Delta E, and entropy. Therefore the result is a trade-off, "
        "not a universal win for one architecture on every metric.",
    )

    subheading(doc, "Qualitative Results")
    add_picture(doc, COLAB_RESULTS / "residual_full" / "residual_comparison_grid.png", 6.0)
    caption(doc, "Figure 7. Residual model test-set examples: turbid input, restored output, and clear reference.")
    add_picture(doc, COLAB_RESULTS / "param_matched_unet" / "results" / "baseline_full" / "baseline_comparison_grid.png", 6.0)
    caption(doc, "Figure 8. Parameter-matched U-Net qualitative examples for capacity-control comparison.")


def add_discussion(doc: Document) -> None:
    heading(doc, "DISCUSSION AND LIMITATIONS")
    para(
        doc,
        "The residual backbone is especially strong on SSIM and Delta E. This suggests better structural consistency and lower "
        "color difference compared with the default baseline. The entropy result also suggests smoother, less noisy outputs.",
    )
    para(
        doc,
        "The capacity-control result prevents overclaiming. A larger U-Net can improve pixel-wise reconstruction metrics. "
        "The final claim should therefore emphasize structural and color-oriented improvement instead of claiming that residual "
        "blocks are best for every metric.",
    )
    bullet(doc, "External datasets are qualitative only because they do not provide paired clear references.")
    bullet(doc, "The supervised dataset is patch-based, so generalization to complex full underwater scenes is limited.")
    bullet(doc, "The implemented model restores single images and does not enforce temporal video consistency.")
    bullet(doc, "Higher resolution and longer training may need additional hyperparameter tuning.")


def add_conclusion(doc: Document) -> None:
    heading(doc, "CONCLUSION")
    para(
        doc,
        "This project implemented a conditional diffusion underwater restoration pipeline and compared a standard U-Net "
        "denoising backbone with a ResNet-style residual backbone. The comparison was controlled by using the same dataset, "
        "split, diffusion objective, training protocol, and metrics.",
    )
    para(
        doc,
        "The residual backbone improves clearly over the default U-Net baseline, especially on SSIM and Delta E. The "
        "parameter-matched U-Net ablation shows that model capacity also matters for MSE, MAE, and PSNR. The final contribution "
        "is therefore a controlled architectural study showing that residual backbones improve structural and color-oriented "
        "restoration behavior in diffusion-based underwater image restoration.",
    )


def add_references(doc: Document) -> None:
    heading(doc, "REFERENCES")
    refs = [
        "[1] J. Ho, A. Jain, and P. Abbeel, Denoising Diffusion Probabilistic Models, NeurIPS, 2020.",
        "[2] O. Ronneberger, P. Fischer, and T. Brox, U-Net: Convolutional Networks for Biomedical Image Segmentation, MICCAI, 2015.",
        "[3] K. He, X. Zhang, S. Ren, and J. Sun, Deep Residual Learning for Image Recognition, CVPR, 2016.",
        "[4] C. Li et al., An Underwater Image Enhancement Benchmark Dataset and Beyond, IEEE TIP, 2020.",
        "[5] F. Iqbal and B. U. Toreyin, Underwater Turbid Image Restoration Using Diffusion Models, project reference paper.",
    ]
    for ref in refs:
        para(doc, ref)


def add_appendix(doc: Document) -> None:
    heading(doc, "APPENDIX")
    subheading(doc, "Pixel-Wise Metric Plots")
    add_picture(doc, REPORT_OUTPUTS / "mse_comparison.png", 5.6)
    caption(doc, "Figure 9. MSE comparison. Lower is better.")
    add_picture(doc, REPORT_OUTPUTS / "psnr_comparison.png", 5.6)
    caption(doc, "Figure 10. PSNR comparison. Higher is better.")
    subheading(doc, "Repository And Deliverables")
    para(doc, "Repository: https://github.com/bedirhanozturk1/Underwater_Resnet_Restoration")
    para(doc, "Final report, presentation, checkpoint documents, metric CSV files, plots, and qualitative grids are stored in the project deliverable folders.")


def add_metric_summary_table(doc: Document) -> None:
    rows = list(csv.DictReader((REPORT_OUTPUTS / "metric_summary.csv").open(encoding="utf-8")))
    table_rows = [["Experiment", "MSE", "MAE", "PSNR", "SSIM", "Delta E", "Entropy"]]
    names = {
        "baseline_128_50": "U-Net 128/50",
        "param_matched_unet_128_50": "Matched U-Net 128/50",
        "residual_128_50": "Residual 128/50",
        "baseline_128_100": "U-Net 128/100",
        "residual_128_100": "Residual 128/100",
        "baseline_256_50": "U-Net 256/50",
        "residual_256_50": "Residual 256/50",
    }
    for row in rows:
        table_rows.append(
            [
                names.get(row["experiment"], row["experiment"]),
                row["mse"],
                row["mae"],
                row["psnr"],
                row["ssim"],
                row["delta_e_cie76"],
                row["entropy"],
            ]
        )
    add_table(doc, table_rows, font_size=7)


def heading(doc: Document, text: str) -> None:
    p = doc.add_heading(text, level=1)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)


def preamble_heading(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    try:
        p.style = "Preamble Title"
    except KeyError:
        p.style = "Heading 1"
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    p.add_run(text)


def subheading(doc: Document, text: str) -> None:
    p = doc.add_heading(text, level=2)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)


def para(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.05
    p.add_run(text)


def bullet(doc: Document, text: str) -> None:
    try:
        p = doc.add_paragraph(style="List Bullet")
        prefix = ""
    except KeyError:
        p = doc.add_paragraph()
        prefix = "- "
    p.paragraph_format.space_after = Pt(2)
    p.add_run(prefix + text)


def add_centered(doc: Document, text: str, size: int, bold: bool = False) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)


def add_spacer(doc: Document, count: int) -> None:
    for _ in range(count):
        doc.add_paragraph()


def add_picture(doc: Document, path: Path, width: float) -> None:
    if not path.exists():
        para(doc, f"Missing figure: {path}")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Inches(width))


def caption(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)


def add_table(doc: Document, rows: list[list[str]], font_size: int = 9) -> None:
    table = doc.add_table(rows=len(rows), cols=max(len(row) for row in rows))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell.text = value
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if r == 0 else WD_ALIGN_PARAGRAPH.LEFT
                for run in paragraph.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(font_size)
                    if r == 0:
                        run.bold = True
                        run.font.color.rgb = RGBColor(31, 78, 121)
    doc.add_paragraph()


def create_presentation_outline() -> None:
    text = """# Final Presentation Outline

## Slide 1 - Title
Enhancing Diffusion-Based Underwater Image Restoration with Residual Networks.

## Slide 2 - Problem
Underwater turbidity causes scattering, low contrast, and color distortion. The task is paired restoration from turbid image to clear/reference image.

## Slide 3 - Dataset
3672 paired images: 2937 train, 367 validation, 368 test. External/unpaired datasets are qualitative only.

## Slide 4 - Method
Conditional diffusion model with the same noising objective. Baseline uses a U-Net denoiser; proposed model uses a ResNet-style residual denoiser.

## Slide 5 - Main Result
Residual improves strongly over the default U-Net baseline, especially on SSIM and Delta E.

## Slide 6 - Capacity Control
Parameter-matched U-Net improves MSE/PSNR. Residual remains better on SSIM, Delta E, and entropy.

## Slide 7 - Qualitative Examples
Show residual comparison grid and parameter-matched U-Net grid.

## Slide 8 - Conclusion
Residual diffusion improves structural and color-oriented restoration, but the result is not a universal win on every metric.
"""
    (DELIVERABLES / "final_presentation_outline.md").write_text(text, encoding="utf-8")


def create_presentation_pptx() -> None:
    prs = Presentation()
    prs.slide_width = PptInches(13.333)
    prs.slide_height = PptInches(7.5)
    add_slide(prs, "Enhancing Diffusion-Based Underwater Image Restoration", ["Residual denoising backbones inside conditional diffusion", "Student ID: 150210321"])
    add_slide(prs, "Problem", ["Turbidity causes scattering, low contrast, and color distortion.", "Task: turbid underwater patch -> clear/reference patch.", "Question: does residual denoising improve the diffusion backbone?"])
    add_picture_slide(prs, "Dataset Example", REPORT_ASSETS / "paired_underwater_patches.png")
    add_slide(prs, "Method", ["Conditional diffusion model predicts noise added to the clean target.", "Baseline: conditional U-Net denoising backbone.", "Proposed: ResNet-style residual denoising backbone.", "Capacity control: parameter-matched U-Net."])
    add_picture_slide(prs, "Training Curves", REPORT_OUTPUTS / "training_loss_curves.png")
    add_slide(prs, "Main Result", ["Residual 128/50 improves default U-Net 128/50.", "SSIM: 0.610758 -> 0.788963.", "Delta E: 29.645203 -> 26.840257.", "MSE reduction: 9.42%."])
    add_picture_slide(prs, "SSIM Comparison", REPORT_OUTPUTS / "ssim_comparison.png")
    add_slide(prs, "Capacity Control", ["Matched U-Net is best on MSE, MAE, and PSNR.", "Residual is best on SSIM, Delta E, and entropy.", "This makes the final claim more honest and stronger."])
    add_picture_slide(prs, "Residual Examples", COLAB_RESULTS / "residual_full" / "residual_comparison_grid.png")
    add_slide(prs, "Conclusion", ["Residual backbone improves structural/color-oriented restoration over the default baseline.", "Parameter matching shows model capacity also matters.", "External datasets are qualitative only because paired references are unavailable."])
    prs.save(DELIVERABLES / "final_presentation_150210321.pptx")


def add_slide(prs: Presentation, title: str, bullets: list[str]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = title
    body = slide.placeholders[1].text_frame
    body.clear()
    for index, bullet_text in enumerate(bullets):
        paragraph = body.paragraphs[0] if index == 0 else body.add_paragraph()
        paragraph.text = bullet_text
        paragraph.level = 0
        paragraph.font.size = PptPt(24)


def add_picture_slide(prs: Presentation, title: str, image_path: Path) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title
    if image_path.exists():
        slide.shapes.add_picture(str(image_path), PptInches(1.05), PptInches(1.15), width=PptInches(11.2))
    else:
        box = slide.shapes.add_textbox(PptInches(1.0), PptInches(2.5), PptInches(11.0), PptInches(1.0))
        box.text_frame.text = f"Missing image: {image_path}"


def create_submission_readme() -> None:
    text = """# Final Submission Notes

This folder contains the final local deliverables.

## Files

- `final_report_150210321.docx`: editable final report.
- `final_report_150210321.pdf`: PDF export of the final report.
- `final_report_150210321_template.docx`: template-based report fallback if the main DOCX is open/locked.
- `final_report_150210321_template.pdf`: PDF export of the template-based fallback report.
- `final_presentation_150210321.pptx`: editable final presentation.
- `final_presentation_150210321.pdf`: PDF export of the presentation.
- `final_presentation_outline.md`: short slide outline.
- `README_FINAL_SUBMISSION.md`: this file.

## GitHub

Repository: https://github.com/bedirhanozturk1/Underwater_Resnet_Restoration

## Reporting Note

Use the capacity-control interpretation. The residual backbone is strongest on SSIM, Delta E, and entropy. The parameter-matched U-Net is slightly stronger on MSE, MAE, and PSNR.
"""
    (DELIVERABLES / "README_FINAL_SUBMISSION.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
