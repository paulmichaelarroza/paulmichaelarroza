from scan_to_text_app import clean_text, extract_section


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
