from pathlib import Path

import streamlit as st

import db
from corretor import MOTIVO_FIXA, ErroCorrecao, aplicar, corrigir
from pdf import extrair_texto

st.set_page_config(page_title="Corretor de Textos", page_icon="✍️", layout="wide")
db.inicializar()


def exibir_resultado(registro: dict, editavel: bool) -> None:
    rid, original, correcoes = registro["id"], registro["texto_original"], registro["correcoes"]
    chave = f"{'edit' if editavel else 'hist'}_{rid}"
    # Automáticas recusadas são as que o autor mandou para o dicionário pessoal.
    automaticas = [c for c in correcoes if c["tipo"] == "automatica" and c["aceita"]]
    sugestoes = [c for c in correcoes if c["tipo"] == "sugestao"]

    # Os textos ficam no topo, mas dependem dos checkboxes renderizados abaixo.
    area_textos = st.container()

    st.subheader(f"Correções aplicadas ({len(automaticas)})")
    if automaticas:
        st.dataframe(
            [{"Original": c["original"], "Corrigido": c["corrigido"], "Motivo": c["motivo"]} for c in automaticas],
            width="stretch",
            hide_index=True,
        )
        if editavel:
            with st.expander("Alguma dessas palavras está certa? (nomes, gírias, termos da história)"):
                escolhidas = st.multiselect(
                    "Não corrigir mais",
                    # Correções fixas são desligadas na aba Dicionário, não aqui.
                    sorted({c["original"] for c in automaticas if c["motivo"] != MOTIVO_FIXA}),
                    key=f"ignorar_{rid}",
                    help="Vão para o dicionário pessoal e a correção é desfeita neste texto.",
                )
                if st.button("Adicionar ao dicionário pessoal", key=f"btn_ignorar_{rid}", disabled=not escolhidas):
                    for palavra in escolhidas:
                        db.adicionar_ignorada(palavra)
                    minusculas = {p.lower() for p in escolhidas}
                    for c in correcoes:
                        if c["tipo"] == "automatica" and c["original"].lower() in minusculas:
                            c["aceita"] = False
                    db.atualizar(rid, aplicar(original, correcoes), correcoes)
                    st.rerun()
    else:
        st.success("Nenhuma correção ortográfica necessária.")

    mudou = False
    if sugestoes and editavel:
        st.subheader(f"Sugestões de concordância ({len(sugestoes)})")
        st.caption("Não são aplicadas automaticamente. Marque as que quiser aceitar.")
        for i, c in enumerate(sugestoes):
            aceita = st.checkbox(
                f"“{c['original']}” → “{c['corrigido']}” — {c['motivo']}",
                value=c["aceita"],
                key=f"sug_{rid}_{i}",
            )
            mudou |= aceita != c["aceita"]
            c["aceita"] = aceita
    elif sugestoes:
        st.subheader(f"Sugestões de concordância ({len(sugestoes)})")
        st.dataframe(
            [
                {
                    "Status": "✅ aceita" if c["aceita"] else "❌ recusada",
                    "Original": c["original"],
                    "Sugestão": c["corrigido"],
                    "Motivo": c["motivo"],
                }
                for c in sugestoes
            ],
            width="stretch",
            hide_index=True,
        )

    if all("offset" in c for c in correcoes):
        corrigido = aplicar(original, correcoes)
    else:  # registro da versão anterior (sem offsets): mantém o texto salvo
        corrigido = registro["texto_corrigido"]
    if mudou or corrigido != registro["texto_corrigido"]:
        registro["texto_corrigido"] = corrigido
        db.atualizar(rid, corrigido, correcoes)

    with area_textos:
        col_orig, col_corr = st.columns(2)
        with col_orig:
            st.markdown("**Original**")
            st.text_area("Original", original, height=400, disabled=True, label_visibility="collapsed", key=f"orig_{chave}")
        with col_corr:
            st.markdown("**Corrigido**")
            # A chave muda junto com o texto para o campo refletir cada checkbox marcado.
            st.text_area(
                "Corrigido", corrigido, height=400, label_visibility="collapsed", key=f"corr_{chave}_{hash(corrigido)}"
            )
            nome = Path(registro["arquivo"]).stem if registro["arquivo"] else "texto"
            st.download_button(
                "Baixar texto corrigido (.txt)",
                corrigido,
                file_name=f"{nome}_corrigido.txt",
                mime="text/plain",
                on_click="ignore",
                key=f"baixar_{chave}",
            )

    if registro["observacoes"].strip():
        st.subheader("Observações de estilo (não aplicadas)")
        st.info(registro["observacoes"])


st.title("✍️ Corretor de Textos")
st.caption("Revisão ortográfica e gramatical preservando o estilo do autor · LanguageTool (offline, gratuito)")

aba_corrigir, aba_historico, aba_dicionario = st.tabs(["Corrigir", "Histórico", "Dicionário"])

with aba_corrigir:
    modo = st.radio("Entrada", ["Colar texto", "Enviar PDF"], horizontal=True, label_visibility="collapsed")
    if modo == "Colar texto":
        texto = st.text_area("Cole ou digite seu texto", height=250, placeholder="Era uma vez...")
    else:
        enviado = st.file_uploader("Envie um PDF com texto (PDFs escaneados não são suportados)", type="pdf")

    # Sem "disabled": o text_area só envia o valor ao perder o foco, então um botão
    # desabilitado engoliria o primeiro clique logo após digitar.
    if st.button("Corrigir texto", type="primary"):
        if modo == "Enviar PDF" and enviado is None:
            st.warning("Envie um arquivo PDF para corrigir.")
        elif modo == "Colar texto" and not texto.strip():
            st.warning("Digite ou cole um texto para corrigir.")
        else:
            with st.spinner(
                "Revisando o texto... (a primeira correção demora mais: o LanguageTool está iniciando;"
                " textos longos podem levar alguns minutos)"
            ):
                arquivo = ""
                try:
                    if modo == "Enviar PDF":
                        arquivo = enviado.name
                        texto = extrair_texto(enviado.getvalue())
                    resultado = corrigir(texto, set(db.listar_ignoradas()), db.listar_fixas())
                except ErroCorrecao as e:
                    st.error(str(e))
                else:
                    registro_id = db.salvar(
                        texto, resultado.texto_corrigido, resultado.correcoes, resultado.observacoes, arquivo
                    )
                    st.session_state["ultimo_id"] = registro_id

    ultimo = db.obter(st.session_state["ultimo_id"]) if "ultimo_id" in st.session_state else None
    if ultimo:
        st.divider()
        exibir_resultado(ultimo, editavel=True)

with aba_historico:
    registros = db.listar()
    if not registros:
        st.write("Nenhuma correção salva ainda.")

    for r in registros:
        previa = r["texto_original"][:80].replace("\n", " ")
        aceitas = sum(c["aceita"] for c in r["correcoes"])
        origem = f"📄 {r['arquivo']} · " if r["arquivo"] else ""
        with st.expander(f"{r['data']} · {origem}{aceitas} correções · {previa}…"):
            if st.button("Excluir", key=f"excluir_{r['id']}"):
                db.excluir(r["id"])
                st.rerun()
            exibir_resultado(r, editavel=False)

with aba_dicionario:
    st.caption("Ajustes que valem para as próximas correções. Maiúsculas e minúsculas são ignoradas.")
    col_ignoradas, col_fixas = st.columns(2)

    with col_ignoradas:
        st.subheader("Palavras aceitas")
        st.caption("Nunca são corrigidas: nomes de personagens, lugares, gírias, termos da história.")
        with st.form("form_ignorada", clear_on_submit=True):
            nova = st.text_input("Palavra ou trecho", placeholder="Aelin")
            if st.form_submit_button("Adicionar") and nova.strip():
                db.adicionar_ignorada(nova)
                st.rerun()
        for palavra in db.listar_ignoradas():
            col_palavra, col_remover = st.columns([5, 1])
            col_palavra.write(palavra)
            if col_remover.button("Remover", key=f"rem_ign_{palavra}"):
                db.remover_ignorada(palavra)
                st.rerun()

    with col_fixas:
        st.subheader("Correções fixas")
        st.caption("Sempre aplicadas, mesmo quando o LanguageTool não marca nada, e com prioridade sobre ele.")
        with st.form("form_fixa", clear_on_submit=True):
            col_de, col_para = st.columns(2)
            de = col_de.text_input("Quando aparecer", placeholder="tava")
            para = col_para.text_input("Trocar por", placeholder="estava")
            if st.form_submit_button("Adicionar") and de.strip() and para.strip():
                db.adicionar_fixa(de, para)
                st.rerun()
        for de, para in db.listar_fixas().items():
            col_regra, col_remover = st.columns([5, 1])
            col_regra.write(f"{de} → {para}")
            if col_remover.button("Remover", key=f"rem_fixa_{de}"):
                db.remover_fixa(de)
                st.rerun()
