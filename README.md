# Scan to Text Application

A Python OCR workflow that can:

1. **Scan one or many image files into text**.
2. **Extract and normalize `net weight` values** (`1,25` ➜ `1.25`).
3. **Save OCR records to a SQLite database**.
4. **Export stored OCR records to Excel (`.xlsx`)**.

## Features

- OCR preprocessing (grayscale + denoise + threshold) to improve readability.
- Batch image processing.
- Net weight extraction from OCR text (`Net Weight`, `NET WT`) with decimal normalization.
- Persistent storage in SQLite.
- Excel export using `openpyxl`.
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

### 1) Scan one image to text

```bash
python scan_to_text_app.py scan-image --input sample.png --output output.txt
```

### 2) Process multiple images (batch)

Print extracted net weights:

```bash
python scan_to_text_app.py process-batch --inputs img1.png img2.png img3.png
```

Process and save to SQLite:

```bash
python scan_to_text_app.py process-batch \
  --inputs img1.png img2.png img3.png \
  --db ocr_records.db \
  --save
```

### 3) Export DB records to Excel

```bash
python scan_to_text_app.py export-excel --db ocr_records.db --output ocr_records.xlsx
```

### 4) Read a specific section from file

```bash
python scan_to_text_app.py read-section \
  --input output.txt \
  --start "Invoice Number:" \
  --end "Footer" \
  --output invoice_section.txt
```

If you omit `--end`, it returns everything after `--start`.

## Run tests

```bash
pytest -q
```
