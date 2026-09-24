"""Parsing dos campos dos formulários de desligamento."""

from __future__ import annotations

import re
from typing import Dict


FIELDS = ("MUNICIPIO", "CPF", "NIS", "NOME", "MOTIVO")


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" \t:;")


def _value_after_label(text: str, label: str) -> str:
    """Retorna o valor da mesma linha ou da primeira linha seguinte preenchida."""
    match = re.search(rf"{label}\s*:\s*([^\r\n]*)", text, re.IGNORECASE)
    if not match:
        return ""
    value = _clean(match.group(1))
    if value:
        return value
    for line in text[match.end() :].splitlines():
        value = _clean(line)
        if value:
            return value
    return ""


def _label_pattern(label: str) -> str:
    tokens = re.findall(r"[\wÀ-ÿ]+|\([^)]*\)", label)
    return r"\s+".join(re.escape(token) for token in tokens)


def _extract_name(text: str) -> str:
    label = _label_pattern("NOME DO RESPONSÁVEL FAMILIAR (RF) A SER DESLIGADO")
    match = re.search(rf"{label}\s*:\s*([^\r\n]*)", text, re.IGNORECASE)
    if not match:
        return ""
    value = _clean(match.group(1))
    if value:
        return re.sub(r"[\d()\-]+$", "", value).strip()
    for line in text[match.end() :].splitlines():
        value = _clean(line)
        if value:
            return re.sub(r"[\d()\-]+$", "", value).strip()
    return ""


def _extract_reason(text: str) -> str:
    heading = re.search(r"MOTIVO\s+DO\s+DESLIGAMENTO", text, re.IGNORECASE)
    if not heading:
        return ""
    section = re.split(
        r"\n\s*(?:ASSINATURA|OBSERVA[CÇ]ÕES?|DATA\s*:|MUNIC[IÍ]PIO\s*:)",
        text[heading.end() :], maxsplit=1, flags=re.IGNORECASE,
    )[0]
    lines = section.splitlines()
    for index, line in enumerate(lines):
        if not re.search(r"\(\s*[xX]\s*\)", line):
            continue
        reason = _clean(re.sub(r"\(\s*[xX]\s*\)", "", line))
        if not reason:
            continue
        if reason.casefold().startswith("outro"):
            for following in lines[index + 1 :]:
                detail = _clean(following)
                if not detail or re.search(r"\(\s*[xX ]\s*\)", detail):
                    continue
                reason = f"{reason}: {detail}"
                break
        return reason
    return ""


def parse_text(text: str) -> Dict[str, str]:
    """Extrai os campos conhecidos sem preencher valores ausentes."""
    municipality = _value_after_label(text, r"MUNIC[IÍ]PIO")
    municipality = re.sub(r"\s+\d+\s*$", "", municipality).strip()
    return {
        "MUNICIPIO": municipality,
        "CPF": re.sub(r"\D", "", _value_after_label(text, r"CPF"))[:11],
        "NIS": re.sub(r"\D", "", _value_after_label(text, r"NIS")),
        "NOME": _extract_name(text),
        "MOTIVO": _extract_reason(text),
    }


def inconsistencies(record: Dict[str, str]) -> list[str]:
    missing = [field for field in FIELDS if not str(record.get(field, "")).strip()]
    if record.get("CPF") and len(str(record["CPF"]).strip()) != 11:
        missing.append("CPF inválido")
    return missing


def status_for(record: Dict[str, str]) -> str:
    return "OK" if not inconsistencies(record) else "REVISAR"