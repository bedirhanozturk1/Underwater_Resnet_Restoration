param(
    [Parameter(Mandatory = $true)]
    [string]$DocumentPath,

    [Parameter(Mandatory = $true)]
    [string]$PdfPath,

    [string]$BackupPath = ""
)

$word = New-Object -ComObject Word.Application
try {
    $word.Visible = $false
    if ($BackupPath) {
        $backupDocument = $word.Documents.Open($DocumentPath, $false, $true)
        $backupDocument.SaveAs2($BackupPath, 16)
        $backupDocument.Close(0)
    }
    $document = $word.Documents.Open($DocumentPath, $false, $false)

    # The first three sections are the cover, contents, and summary. Format the body only.
    for ($sectionIndex = 4; $sectionIndex -le $document.Sections.Count; $sectionIndex++) {
        $section = $document.Sections.Item($sectionIndex)
        $section.PageSetup.LeftMargin = 36
        $section.PageSetup.RightMargin = 36
        $section.PageSetup.TopMargin = 74
        $section.PageSetup.BottomMargin = 26
        $section.PageSetup.HeaderDistance = 0
        $section.PageSetup.FooterDistance = 16.5

        $header = $section.Headers.Item(1)
        $header.LinkToPrevious = $false
        $header.Range.Text = @"
Istanbul Technical University
Faculty of Computer and Informatics
Department of Artificial Intelligence and Data Engineering
Artificial Intelligence and Data Engineering Undergraduate Programme
"@
        $header.Range.Font.Name = "Calibri"
        $header.Range.Font.Size = 8
        $header.Range.ParagraphFormat.Alignment = 1
        $header.Range.ParagraphFormat.SpaceBefore = 0
        $header.Range.ParagraphFormat.SpaceAfter = 0
        $header.Range.ParagraphFormat.LineSpacingRule = 0
    }

    foreach ($paragraph in $document.Paragraphs) {
        $range = $paragraph.Range
        $page = $range.Information(3)
        if ($page -lt 4) {
            continue
        }

        $text = $range.Text.Trim()
        if ($paragraph.OutlineLevel -eq 1) {
            $range.Font.Name = "Arial"
            $range.Font.Size = 16
            $range.Font.Bold = $true
            $paragraph.Alignment = 0
            $paragraph.LeftIndent = 63.25
            $paragraph.SpaceBefore = 4
            $paragraph.SpaceAfter = 0
            $paragraph.PageBreakBefore = 0
            $paragraph.KeepWithNext = 0
        }
        elseif ($paragraph.OutlineLevel -eq 2) {
            $range.Font.Name = "Arial"
            $range.Font.Size = 14
            $range.Font.Bold = $true
            $paragraph.Alignment = 0
            $paragraph.LeftIndent = 63.1
            $paragraph.SpaceBefore = 12
            $paragraph.SpaceAfter = 0
            $paragraph.PageBreakBefore = 0
            $paragraph.KeepWithNext = 0
        }
        elseif ($text.Length -eq 0 -and -not $range.Information(12)) {
            $range.Font.Size = 1
            $paragraph.SpaceBefore = 0
            $paragraph.SpaceAfter = 0
            $paragraph.LineSpacingRule = 4
            $paragraph.LineSpacing = 1
        }
        elseif ($paragraph.Alignment -eq 3 -and $range.Font.Size -eq 12 -and -not $range.Information(12)) {
            $range.Font.Name = "Calibri"
            $range.Font.Size = 12
            $paragraph.LeftIndent = 36
            $paragraph.RightIndent = 36
            $paragraph.FirstLineIndent = 0
            $paragraph.SpaceBefore = 0
            $paragraph.SpaceAfter = 0
            $paragraph.LineSpacingRule = 0
            $paragraph.LineSpacing = 12
        }
    }

    $document.Repaginate()
    foreach ($contents in $document.TablesOfContents) {
        $contents.Update()
    }
    if ($document.TablesOfContents.Count -eq 0) {
        $headingPages = @{}
        foreach ($paragraph in $document.Paragraphs) {
            if ($paragraph.OutlineLevel -eq 1 -or $paragraph.OutlineLevel -eq 2) {
                $heading = $paragraph.Range.Text.Trim().ToUpperInvariant()
                $headingPages[$heading] = $paragraph.Range.Information(3) - 3
            }
        }
        foreach ($paragraph in $document.Paragraphs) {
            if ($paragraph.Range.Information(3) -ne 2) {
                continue
            }
            $tocText = $paragraph.Range.Text.Trim()
            $match = [regex]::Match($tocText, "^(?<number>\d+(?:\.\d+)?)\s+(?<title>.+)\t\d+$")
            if (-not $match.Success) {
                continue
            }
            $titleKey = $match.Groups["title"].Value.ToUpperInvariant()
            if ($headingPages.ContainsKey($titleKey)) {
                $textRange = $paragraph.Range.Duplicate
                $textRange.End = $textRange.End - 1
                $textRange.Text = "$($match.Groups['number'].Value)  $($match.Groups['title'].Value)`t$($headingPages[$titleKey])"
            }
        }
    }
    $document.Fields.Update() | Out-Null
    $document.Repaginate()
    foreach ($contents in $document.TablesOfContents) {
        $contents.UpdatePageNumbers()
    }
    $document.Save()
    $document.ExportAsFixedFormat($PdfPath, 17)
    $document.Close(0)
}
finally {
    $word.Quit()
}
