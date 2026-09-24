"""Formatos de download da tabela processada."""

from __future__ import annotations

from io import BytesIO

import pandas as pd


def to_csv(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")


def to_xlsx(dataframe: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Desligamentos")
    return buffer.getvalue()