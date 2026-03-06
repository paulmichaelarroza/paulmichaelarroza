#!/usr/bin/env python3
"""Scan-to-text utility with section extraction helpers."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Optional


class OCRDependencyError(RuntimeError):
    """Raised when OCR dependencies are not available."""


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def clean_text(text: str) -> str:
    """Improve readability by collapsing noisy spaces and empty lines."""
    text = _normalize_newlines(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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


def _write_output(text: str, output: Optional[Path]) -> None:
    if output:
        output.write_text(text, encoding="utf-8")
    else:
        print(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan image to text and read specific sections from text files."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan-image", help="Extract text from an image")
    scan_parser.add_argument("--input", type=Path, required=True, help="Path to image file")
    scan_parser.add_argument("--output", type=Path, help="Write extracted text to this file")
    scan_parser.add_argument(
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
    section_parser.add_argument(
        "--start", required=True, help="Starting marker (required)"
    )
    section_parser.add_argument("--end", help="Ending marker (optional)")
    section_parser.add_argument("--output", type=Path, help="Write section to this file")
    section_parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Use case-sensitive marker matching",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan-image":
        text = ocr_image_to_text(args.input, psm=args.psm)
        _write_output(text, args.output)
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

    parser.error("Unsupported command")


if __name__ == "__main__":
    main()
