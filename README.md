# Scan to Text Application

A simple Python application that can:

1. **Scan image files into text** (OCR) with readability cleanup.
2. **Read a specific section** from text content using start/end markers.

## Features

- OCR preprocessing (grayscale + denoise + threshold) to improve readability.
- Text cleanup to remove noisy spaces and extra blank lines.
- Section extraction by marker:
  - Start marker required
  - End marker optional
  - Case-insensitive by default

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Note: OCR requires the **Tesseract** binary installed in your OS.

## Usage

### 1) Scan image to text

```bash
python scan_to_text_app.py scan-image --input sample.png --output output.txt
```

Optional OCR page segmentation mode:

```bash
python scan_to_text_app.py scan-image --input sample.png --psm 6
```

### 2) Read a specific section from file

```bash
python scan_to_text_app.py read-section \
  --input output.txt \
  --start "Invoice Number:" \
  --end "Footer" \
  --output invoice_section.txt
```

If you omit `--end`, it returns everything after `--start`.

### 3) Case-sensitive matching

```bash
python scan_to_text_app.py read-section \
  --input output.txt \
  --start "Exact Header" \
  --case-sensitive
```

## Run tests

```bash
pytest -q
```
