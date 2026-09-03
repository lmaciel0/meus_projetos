import pandas as pd

from exports import to_csv, to_xlsx
from parser import parse_text, status_for


TEXT = """
MUNICÍPIO: SÃO GONÇALO
CPF: 001.234.567-89
NIS: 000123456789
NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO: MARIA DA SILVA
MOTIVO DO DESLIGAMENTO
( ) Mudança para outro Estado
(X) OUTRO
Mudança de renda da família
"""


def test_parse_preserves_identifiers_and_other_reason():
    record = parse_text(TEXT)
    assert record == {
        "MUNICIPIO": "SÃO GONÇALO",
        "CPF": "00123456789",
        "NIS": "000123456789",
        "NOME": "MARIA DA SILVA",
        "MOTIVO": "OUTRO: Mudança de renda da família",
    }
    assert status_for(record) == "OK"


def test_missing_field_requires_review():
    assert status_for({"CPF": "123"}) == "REVISAR"


def test_exports_are_downloadable_formats():
    dataframe = pd.DataFrame([{"CPF": "00123456789", "STATUS": "OK"}])
    assert to_csv(dataframe).startswith(b"\xef\xbb\xbfCPF")
    assert to_xlsx(dataframe)[:2] == b"PK"