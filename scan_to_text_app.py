#!/usr/bin/env python3
"""Scan-to-text utility with OCR extraction and net-weight processing."""

from __future__ import annotations

import argparse
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence


class OCRDependencyError(RuntimeError):
    """Raised when OCR dependencies are not available."""


@dataclass
class OCRRecord:
    image_path: str
    extracted_text: str
    net_weight: Optional[str]


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def clean_text(text: str) -> str:
    """Improve readability by collapsing noisy spaces and empty lines."""
    text = _normalize_newlines(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_decimal(value: str) -> str:
    """Normalize decimal separator to period when a comma is used."""
    raw = value.strip()
    if "," in raw and "." not in raw:
        return raw.replace(",", ".")
    return raw


def extract_net_weight(text: str) -> Optional[str]:
    """Extract net weight value from OCR text and normalize decimal format."""
    source = clean_text(text)

    marker_patterns = [
        r"\bnet\s*weight\b\s*[:=-]?\s*([0-9]+(?:[\.,][0-9]+)?)",
        r"\bnet\s*wt\b\s*[:=-]?\s*([0-9]+(?:[\.,][0-9]+)?)",
    ]

    for pattern in marker_patterns:
        match = re.search(pattern, source, flags=re.IGNORECASE)
        if match:
            return normalize_decimal(match.group(1))

    return None


def extract_section(
    text: str,
    start_marker: str,
    end_marker: Optional[str] = None,
    ignore_case: bool = True,
) -> str:
    """Return text between start_marker and optional end_marker.

    If end_marker is omitted, text from start marker to the end is returned.
    """
    if not start_marker:
        raise ValueError("start_marker is required")

    source = _normalize_newlines(text)
    flags = re.IGNORECASE if ignore_case else 0

    start_match = re.search(re.escape(start_marker), source, flags=flags)
    if not start_match:
        raise ValueError(f"Start marker not found: {start_marker!r}")

    section_start = start_match.end()

    if end_marker:
        end_match = re.search(re.escape(end_marker), source[section_start:], flags=flags)
        if not end_match:
            raise ValueError(f"End marker not found: {end_marker!r}")
        result = source[section_start : section_start + end_match.start()]
    else:
        result = source[section_start:]

    return clean_text(result)


def ocr_image_to_text(image_path: Path, psm: int = 6) -> str:
    """Extract text from an image using OCR with basic preprocessing."""
    try:
        import cv2  # type: ignore
        import pytesseract  # type: ignore
    except ImportError as exc:
        raise OCRDependencyError(
            "Install dependencies with: pip install -r requirements.txt"
        ) from exc

    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.medianBlur(gray, 3)
    processed = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        12,
    )

    custom_config = f"--oem 3 --psm {psm}"
    text = pytesseract.image_to_string(processed, config=custom_config)
    return clean_text(text)


def init_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ocr_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                net_weight TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_records(db_path: Path, records: Sequence[OCRRecord]) -> int:
    if not records:
        return 0

    init_db(db_path)
    rows = [
        (
            record.image_path,
            record.extracted_text,
            record.net_weight,
            datetime.now(timezone.utc).isoformat(),
        )
        for record in records
    ]

    with sqlite3.connect(db_path) as connection:
        connection.executemany(
            """
            INSERT INTO ocr_records (image_path, extracted_text, net_weight, created_at)
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()

    return len(rows)


def process_images(image_paths: Sequence[Path], psm: int = 6) -> list[OCRRecord]:
    records: list[OCRRecord] = []
    for image_path in image_paths:
        text = ocr_image_to_text(image_path, psm=psm)
        records.append(
            OCRRecord(
                image_path=str(image_path),
                extracted_text=text,
                net_weight=extract_net_weight(text),
            )
        )
    return records


def export_to_excel(db_path: Path, excel_path: Path) -> int:
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise RuntimeError(
            "openpyxl is required to export Excel files. Install dependencies first."
        ) from exc

    init_db(db_path)
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, image_path, net_weight, extracted_text, created_at
            FROM ocr_records
            ORDER BY id ASC
            """
        ).fetchall()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "OCR Records"
    worksheet.append(["ID", "Image Path", "Net Weight", "Extracted Text", "Created At"])

    for row in rows:
        worksheet.append(list(row))

    workbook.save(excel_path)
    return len(rows)


def _write_output(text: str, output: Optional[Path]) -> None:
    if output:
        output.write_text(text, encoding="utf-8")
    else:
        print(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan images to text, extract net weights, save to DB, and export to Excel."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan-image", help="Extract text from one image")
    scan_parser.add_argument("--input", type=Path, required=True, help="Path to image file")
    scan_parser.add_argument("--output", type=Path, help="Write extracted text to this file")
    scan_parser.add_argument(
        "--psm",
        type=int,
        default=6,
        help="Tesseract page segmentation mode (default: 6)",
    )

    batch_parser = subparsers.add_parser(
        "process-batch",
        help="Process multiple images, extract net weights, and optionally save records",
    )
    batch_parser.add_argument(
        "--inputs",
        type=Path,
        nargs="+",
        required=True,
        help="One or more image paths",
    )
    batch_parser.add_argument("--db", type=Path, default=Path("ocr_records.db"))
    batch_parser.add_argument("--save", action="store_true", help="Persist records into database")
    batch_parser.add_argument(
        "--psm",
        type=int,
        default=6,
        help="Tesseract page segmentation mode (default: 6)",
    )

    section_parser = subparsers.add_parser(
        "read-section", help="Read a specific section in a text file"
    )
    section_parser.add_argument(
        "--input", type=Path, required=True, help="Path to source text file"
    )
    section_parser.add_argument("--start", required=True, help="Starting marker (required)")
    section_parser.add_argument("--end", help="Ending marker (optional)")
    section_parser.add_argument("--output", type=Path, help="Write section to this file")
    section_parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Use case-sensitive marker matching",
    )

    export_parser = subparsers.add_parser("export-excel", help="Export DB records into an Excel file")
    export_parser.add_argument("--db", type=Path, default=Path("ocr_records.db"))
    export_parser.add_argument("--output", type=Path, required=True, help="Output .xlsx file")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan-image":
        text = ocr_image_to_text(args.input, psm=args.psm)
        _write_output(text, args.output)
        return

    if args.command == "process-batch":
        records = process_images(args.inputs, psm=args.psm)
        if args.save:
            inserted = save_records(args.db, records)
            print(f"Processed {len(records)} image(s). Saved {inserted} record(s) to {args.db}.")
        else:
            for record in records:
                print(f"{record.image_path}: net_weight={record.net_weight or 'NOT_FOUND'}")
        return

    if args.command == "read-section":
        source = args.input.read_text(encoding="utf-8")
        section = extract_section(
            source,
            start_marker=args.start,
            end_marker=args.end,
            ignore_case=not args.case_sensitive,
        )
        _write_output(section, args.output)
        return

    if args.command == "export-excel":
        exported = export_to_excel(args.db, args.output)
        print(f"Exported {exported} record(s) to {args.output}")
        return

    parser.error("Unsupported command")


if __name__ == "__main__":
    main()
