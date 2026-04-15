from pathlib import Path

import pytest

from scan_to_text_app import (
    clean_text,
    extract_net_weight,
    extract_section,
    export_to_excel,
    save_records,
    OCRRecord,
)


def test_clean_text_normalizes_spacing_and_blank_lines():
    raw = "This   is\t a  test.\n\n\nNew   line."
    assert clean_text(raw) == "This is a test.\n\nNew line."


def test_extract_section_with_end_marker():
    source = "Header\nInvoice Number: 12345\nTotal: 500\nFooter"
    result = extract_section(source, "Invoice Number:", "Footer")
    assert result == "12345\nTotal: 500"


def test_extract_section_without_end_marker():
    source = "Start\nSection begins here\nLine 2"
    result = extract_section(source, "Section")
    assert result == "begins here\nLine 2"


def test_extract_section_missing_start_raises_error():
    source = "Document content"
    try:
        extract_section(source, "NOT_FOUND")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Start marker not found" in str(exc)


def test_extract_net_weight_converts_comma_decimal_to_period():
    text = "Product Label\nNet Weight: 1,25 kg"
    assert extract_net_weight(text) == "1.25"


def test_extract_net_weight_retains_period_decimal():
    text = "NET WT 2.50 L"
    assert extract_net_weight(text) == "2.50"


def test_save_records_and_export_to_excel(tmp_path: Path):
    pytest.importorskip("openpyxl")
    db_path = tmp_path / "ocr_records.db"
    excel_path = tmp_path / "ocr_records.xlsx"

    records = [
        OCRRecord(image_path="a.png", extracted_text="Net Weight: 1,25 kg", net_weight="1.25"),
        OCRRecord(image_path="b.png", extracted_text="Net Weight: 2.00 kg", net_weight="2.00"),
    ]

    inserted = save_records(db_path, records)
    assert inserted == 2

    exported = export_to_excel(db_path, excel_path)
    assert exported == 2
    assert excel_path.exists()
