---
name: pdf-to-markdown
description: >
  Converts PDF files to clean markdown using the marker library.
  Use when the user mentions PDFs, says "extract text from PDF", "convert PDF",
  "read this PDF", "parse PDF", or provides a .pdf file path. Also triggers on
  "PDF to text", "PDF to markdown", or "what does this PDF say".
  Do NOT use for images, DOCX, XLSX, or non-PDF files.
allowed-tools: Bash(uv run *)
---

Convert the PDF at the given path to markdown.

## Usage

```bash
uv run --script SKILL_DIR/scripts/convert.py "$ARGUMENTS"
```

Where `SKILL_DIR` is the directory containing this skill (use the resolved path from the skill's location).

The script uses PEP 723 inline metadata to manage its own dependencies (marker-pdf), so it runs in an isolated environment.

The script:
1. Takes a PDF file path as input
2. Converts it to markdown using the marker library
3. Writes the output to `<input-name>.md` alongside the original PDF
4. Prints the markdown content to stdout

## After Conversion

Once converted, read the markdown output and work with the content as requested by the user.
