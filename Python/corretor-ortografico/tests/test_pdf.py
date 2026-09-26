import io

import pytest
from pypdf import PdfWriter

from corretor import ErroCorrecao
from pdf import extrair_texto, normalizar


def _pdf_com_texto(*paginas: list[str]) -> bytes:
    """PDF mínimo com uma linha de texto por item, em Helvetica (WinAnsi, cobre acentos)."""
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        None,  # /Pages, preenchido depois de saber os ids das páginas
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    kids = []
    for linhas in paginas:
        conteudo = b"BT /F1 12 Tf 14 TL 50 780 Td "
        for linha in linhas:
            escapada = linha.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            conteudo += b"(" + escapada.encode("cp1252") + b") Tj T* "
        conteudo += b"ET"
        objetos.append(b"<< /Length %d >>\nstream\n" % len(conteudo) + conteudo + b"\nendstream")
        objetos.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>" % len(objetos)
        )
        kids.append(len(objetos))
    objetos[1] = b"<< /Type /Pages /Kids [%s] /Count %d >>" % (
        b" ".join(b"%d 0 R" % k for k in kids),
        len(kids),
    )

    saida, offsets = b"%PDF-1.4\n", []
    for i, obj in enumerate(objetos, start=1):
        offsets.append(len(saida))
        saida += b"%d 0 obj\n" % i + obj + b"\nendobj\n"
    inicio_xref = len(saida)
    saida += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    saida += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    saida += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objetos) + 1, inicio_xref)
    return saida


# --- normalizar ---------------------------------------------------------------


def test_junta_linhas_do_mesmo_paragrafo():
    assert normalizar("Era uma vez uma\nmenina que morava\nna floresta.") == "Era uma vez uma menina que morava na floresta."


def test_junta_palavra_hifenizada_na_quebra():
    assert normalizar("Ela caminhava pela estra-\nda de terra.") == "Ela caminhava pela estrada de terra."


def test_linha_em_branco_separa_paragrafos():
    assert normalizar("Primeiro parágrafo\ncontinua.\n\nSegundo parágrafo.") == (
        "Primeiro parágrafo continua.\n\nSegundo parágrafo."
    )


def test_travessao_de_dialogo_inicia_novo_paragrafo():
    texto = "Ele olhou para ela.\n— Vem? perguntou ele.\n— Vou — respondeu."
    assert normalizar(texto) == "Ele olhou para ela.\n\n— Vem? perguntou ele.\n\n— Vou — respondeu."


def test_remove_linhas_so_com_numero_de_pagina():
    assert normalizar("Fim do capítulo\n12\ncontinua aqui.") == "Fim do capítulo continua aqui."


def test_normaliza_espacos_e_quebras_do_windows():
    assert normalizar("  Um   texto \r\ncom  espaços.  ") == "Um texto com espaços."


# --- extrair_texto --------------------------------------------------------------


def test_extrai_texto_de_varias_paginas_com_acentos():
    dados = _pdf_com_texto(["Era uma vez uma", "menina chamada Conceição"], ["que morava na floresta."])
    assert extrair_texto(dados) == "Era uma vez uma menina chamada Conceição que morava na floresta."


def test_pdf_sem_texto_da_erro_amigavel():
    escritor = PdfWriter()
    escritor.add_blank_page(width=595, height=842)
    buf = io.BytesIO()
    escritor.write(buf)
    with pytest.raises(ErroCorrecao, match="escaneado"):
        extrair_texto(buf.getvalue())


def test_pdf_com_senha_da_erro_amigavel():
    escritor = PdfWriter()
    escritor.add_blank_page(width=595, height=842)
    escritor.encrypt("segredo")
    buf = io.BytesIO()
    escritor.write(buf)
    with pytest.raises(ErroCorrecao, match="senha"):
        extrair_texto(buf.getvalue())


def test_arquivo_invalido_da_erro_amigavel():
    with pytest.raises(ErroCorrecao, match="ler o PDF"):
        extrair_texto(b"isto nao e um pdf")
