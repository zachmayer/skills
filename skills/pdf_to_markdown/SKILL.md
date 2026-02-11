---
name: pdf_to_markdown
description: >
  Convert PDF files to clean markdown using marker. Use when the user wants to
  extract text from a PDF, convert a PDF to markdown for processing, or needs
  to read a PDF's content. Do NOT use for images, DOCX, or non-PDF files.
allowed-tools: Bash(uv run *)
---

Convert the PDF at the given path to markdown.

## Usage

```bash
uv run --directory SKILL_DIR python scripts/convert.py "$ARGUMENTS"
```

Where `SKILL_DIR` is the directory containing this skill (use the resolved path from the skill's location).

The script:
1. Takes a PDF file path as input
2. Converts it to markdown using the marker library
3. Writes the output to `<input-name>.md` alongside the original PDF
4. Prints the markdown content to stdout

## After Conversion

Once converted, read the markdown output and work with the content as requested by the user.
