"""Aplicação web local para leitura de desligamentos do CMIC."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from exports import to_csv, to_xlsx
from parser import FIELDS, inconsistencies, status_for
from processing import DISPLAY_COLUMNS, process_uploads


st.set_page_config(page_title="Leitor de desligamentos", page_icon="CMIC", layout="wide")
st.markdown(
    """
    <style>
    .block-container { max-width: 1400px; padding-top: 2rem; }
    [data-testid="stMetric"] { border: 1px solid #d9e2e8; padding: .8rem; border-radius: .5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _empty_dataframe() -> pd.DataFrame:
    return pd.DataFrame(columns=DISPLAY_COLUMNS)


def _refresh_status(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe.copy()
    for column in DISPLAY_COLUMNS:
        if column not in result:
            result[column] = ""
    for field in [*FIELDS, "ARQUIVO", "Referencia", "STATUS"]:
        result[field] = result[field].fillna("").astype(str)
    result["STATUS"] = result.apply(lambda row: status_for(row.to_dict()), axis=1)
    return result[DISPLAY_COLUMNS]


def _current_issues(dataframe: pd.DataFrame) -> list[dict[str, str]]:
    return [
        {"ARQUIVO": row["ARQUIVO"], "INCONSISTÊNCIAS": ", ".join(inconsistencies(row.to_dict()))}
        for _, row in dataframe.iterrows()
        if inconsistencies(row.to_dict())
    ]


if "records" not in st.session_state:
    st.session_state.records = _empty_dataframe()
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

st.title("Leitor de desligamentos")
st.caption("Cartão Mais Infância Ceará | extração local de PDFs")

upload_columns = st.columns([4, 1])
uploads = upload_columns[0].file_uploader(
    "Selecione os PDFs de desligamento",
    type=["pdf"],
    accept_multiple_files=True,
    key=f"pdf_uploader_{st.session_state.uploader_key}",
)
if upload_columns[1].button("Limpar dados", use_container_width=True):
    st.session_state.records = _empty_dataframe()
    st.session_state.pop("initial_issues", None)
    st.session_state.uploader_key += 1
    st.rerun()
ocr_enabled = st.checkbox("Usar OCR quando o PDF não tiver texto selecionável", value=True)

if st.button("Processar arquivos", type="primary", disabled=not uploads):
    progress_bar = st.progress(0, text="Preparando arquivos...")

    def update_progress(processed: int) -> None:
        progress_bar.progress(processed / len(uploads), text=f"Processando {processed} de {len(uploads)}...")

    records, issues = process_uploads(uploads, progress=update_progress, ocr_enabled=ocr_enabled)
    st.session_state.records = records
    st.session_state.initial_issues = issues
    progress_bar.progress(1.0, text="Processamento concluído")

dataframe = _refresh_status(st.session_state.records)
st.session_state.records = dataframe

if dataframe.empty:
    st.info("Envie um ou mais PDFs e clique em Processar arquivos para começar.")
else:
    ok_count = int((dataframe["STATUS"] == "OK").sum())
    review_count = int((dataframe["STATUS"] == "REVISAR").sum())
    metric_columns = st.columns(3)
    metric_columns[0].metric("Arquivos", len(dataframe))
    metric_columns[1].metric("OK", ok_count)
    metric_columns[2].metric("REVISAR", review_count)

    st.subheader("Filtros")
    filters = st.columns(3)
    municipality_options = sorted(value for value in dataframe["MUNICIPIO"].unique() if value)
    reason_options = sorted(value for value in dataframe["MOTIVO"].unique() if value)
    selected_municipalities = filters[0].multiselect("Município", municipality_options)
    selected_reasons = filters[1].multiselect("Motivo", reason_options)
    selected_status = filters[2].multiselect("Status", ["OK", "REVISAR"])

    filtered = dataframe.copy()
    if selected_municipalities:
        filtered = filtered[filtered["MUNICIPIO"].isin(selected_municipalities)]
    if selected_reasons:
        filtered = filtered[filtered["MOTIVO"].isin(selected_reasons)]
    if selected_status:
        filtered = filtered[filtered["STATUS"].isin(selected_status)]

    st.subheader("Resultados")
    display_filtered = filtered.copy()
    display_filtered["STATUS"] = display_filtered["STATUS"].map(
        {"OK": "✅ OK", "REVISAR": "⚠️ REVISAR"}
    ).fillna(display_filtered["STATUS"])
    edited = st.data_editor(
        display_filtered,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["ARQUIVO", "Referencia", "STATUS"],
        column_config={
            "ARQUIVO": st.column_config.TextColumn("Arquivo", width="medium"),
            "Referencia": st.column_config.TextColumn("Referencia", width="small"),
            "MUNICIPIO": st.column_config.TextColumn("Município"),
            "CPF": st.column_config.TextColumn("CPF", help="Mantido como texto com 11 dígitos"),
            "NIS": st.column_config.TextColumn("NIS"),
            "NOME": st.column_config.TextColumn("Nome", width="large"),
            "MOTIVO": st.column_config.TextColumn("Motivo", width="large"),
            "STATUS": st.column_config.TextColumn("Status", help="✅ indica registro completo; ⚠️ requer revisão"),
        },
        key="records_editor",
    )
    editable_columns = list(FIELDS)
    if not edited[editable_columns].equals(filtered[editable_columns]):
        st.session_state.records.loc[edited.index, editable_columns] = edited[editable_columns]
        st.session_state.records = _refresh_status(st.session_state.records)
        st.rerun()

    issues = _current_issues(st.session_state.records)
    if issues:
        with st.expander(f"Inconsistências ({len(issues)})", expanded=True):
            st.dataframe(pd.DataFrame(issues), hide_index=True, use_container_width=True)

    st.subheader("Downloads")
    download_columns = st.columns(3)
    download_columns[0].download_button("Baixar XLSX", to_xlsx(st.session_state.records), "desligamentos.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    download_columns[1].download_button("Baixar CSV UTF-8", to_csv(st.session_state.records), "desligamentos.csv", "text/csv; charset=utf-8")
    review_data = st.session_state.records[st.session_state.records["STATUS"] == "REVISAR"]
    download_columns[2].download_button("Baixar somente REVISAR", to_xlsx(review_data), "desligamentos_revisar.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", disabled=review_data.empty)