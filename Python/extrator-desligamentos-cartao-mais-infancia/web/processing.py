"""Orquestra processamento dos uploads e montagem do DataFrame."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd

from parser import FIELDS, inconsistencies, parse_text, status_for
from pdf_extractor import PDFExtractor


DISPLAY_COLUMNS = ["ARQUIVO", *FIELDS, "STATUS"]


def process_uploads(
    uploads: Iterable[object],
    progress: Callable[[int], None] | None = None,
    ocr_enabled: bool = True,
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    rows: list[dict[str, str]] = []
    issues: list[dict[str, object]] = []
    uploads = list(uploads)
    extractor = PDFExtractor(ocr_enabled=ocr_enabled)
    for index, upload in enumerate(uploads, start=1):
        filename = str(getattr(upload, "name", "arquivo.pdf"))
        row = {field: "" for field in FIELDS}
        row["ARQUIVO"] = filename
        try:
            with tempfile.TemporaryDirectory(prefix="leitor_desligamentos_") as temp_dir:
                path = Path(temp_dir) / Path(filename).name
                path.write_bytes(upload.getvalue())
                row.update(parse_text(extractor.extract(path)))
        except Exception as error:
            issues.append({"ARQUIVO": filename, "INCONSISTÊNCIAS": f"erro de processamento: {error}"})
        row["STATUS"] = status_for(row)
        missing = inconsistencies(row)
        if missing:
            issues.append({"ARQUIVO": filename, "INCONSISTÊNCIAS": ", ".join(missing)})
        rows.append(row)
        if progress:
            progress(index)
    return pd.DataFrame(rows, columns=DISPLAY_COLUMNS), issues