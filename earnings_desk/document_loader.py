"""Extract readable text from supported uploaded earnings documents."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re


class DocumentReadError(ValueError):
    """Raised when an uploaded report cannot be converted to text."""


LABELS = {
    "company": "Company",
    "company name": "Company",
    "period": "Period",
    "quarter": "Period",
    "revenue": "Revenue",
    "total revenue": "Revenue",
    "net income": "Net income",
    "net profit": "Net income",
    "operating margin": "Operating margin",
    "operating profit margin": "Operating margin",
    "guidance": "Guidance",
    "outlook": "Outlook",
    "risk": "Risk",
}


def extract_document_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(content)
    if suffix == ".xlsx":
        return _read_xlsx(content)
    if suffix == ".xls":
        return _read_xls(content)
    raise DocumentReadError("Upload a PDF, XLSX, or XLS file.")


def _read_pdf(content: bytes) -> str:
    from pypdf import PdfReader

    try:
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise DocumentReadError("This PDF could not be read. Check that it opens normally and is not password-protected.") from exc
    text = "\n".join(page for page in pages if page.strip())
    if not text.strip():
        raise DocumentReadError("This PDF has no selectable text. Scanned image PDFs need OCR before analysis.")
    return _normalize_pdf_labels(text)


def _normalize_pdf_labels(text: str) -> str:
    lines = []
    for raw in text.splitlines():
        line = " ".join(raw.split())
        if not line:
            continue
        match = re.match(
            r"^(Total\s+Revenue|Net\s+Profit|Net\s+Income|Operating\s+Profit\s+Margin|Operating\s+Margin|Company\s+Name|Company|Period|Quarter|Revenue|Guidance|Outlook|Risk)\s*(?::|\||\t|\s{2,})\s*(.*)$",
            line,
            re.IGNORECASE,
        )
        if match:
            label = re.sub(r"\s+", " ", match.group(1)).lower()
            canonical = LABELS.get(label, match.group(1))
            value = match.group(2).strip(" :|\t")
            lines.append(f"{canonical}: {value}" if value else f"{canonical}:")
        else:
            lines.append(line)
    return "\n".join(lines)


def _read_xlsx(content: bytes) -> str:
    from openpyxl import load_workbook

    try:
        workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
        return _format_sheets(
            (
                (sheet.title, [_xlsx_value(cell) for cell in row])
                for sheet in workbook.worksheets
                for row in sheet.iter_rows()
            )
        )
    except Exception as exc:
        raise DocumentReadError("This Excel workbook could not be read. Try saving it as .xlsx first.") from exc


def _xlsx_value(cell) -> str:
    value = cell.value
    if value is None:
        return ""
    if isinstance(value, float) and "%" in (cell.number_format or ""):
        return f"{value * 100:g}%"
    return str(value).strip()


def _read_xls(content: bytes) -> str:
    import xlrd

    try:
        workbook = xlrd.open_workbook(file_contents=content)
        return _format_sheets(
            (sheet.name, [sheet.cell_value(row, col) for col in range(sheet.ncols)])
            for sheet in workbook.sheets()
            for row in range(sheet.nrows)
        )
    except Exception as exc:
        raise DocumentReadError("This .xls workbook could not be read. Try saving it as .xlsx first.") from exc


def _format_sheets(rows) -> str:
    lines: list[str] = []
    current_sheet = None
    for sheet_name, raw_values in rows:
        values = [_clean_value(value) for value in raw_values]
        values = [value for value in values if value]
        if not values:
            continue
        if sheet_name != current_sheet:
            lines.append(f"Worksheet: {sheet_name}")
            current_sheet = sheet_name
        first = values[0].strip().rstrip(":").lower()
        canonical = LABELS.get(first)
        if canonical and len(values) > 1:
            lines.append(f"{canonical}: {'; '.join(values[1:])}")
        elif canonical and len(values) == 1:
            lines.append(f"{canonical}: {values[0]}")
        else:
            lines.append(" | ".join(values))
    text = "\n".join(lines).strip()
    if not text:
        raise DocumentReadError("No populated cells were found in this workbook.")
    return text


def _clean_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()
