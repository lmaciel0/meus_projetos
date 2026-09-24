import streamlit as st

import db
from corretor import MODELO, ErroCorrecao, corrigir

st.set_page_config(page_title="Corretor de Textos", page_icon="✍️", layout="wide")
db.inicializar()


def exibir_resultado(chave: str, original: str, corrigido: str, correcoes: list[dict], observacoes: str) -> None:
    col_orig, col_corr = st.columns(2)
    with col_orig:
        st.markdown("**Original**")
        st.text_area("Original", original, height=400, disabled=True, label_visibility="collapsed", key=f"orig_{chave}")
    with col_corr:
        st.markdown("**Corrigido**")
        st.text_area("Corrigido", corrigido, height=400, label_visibility="collapsed", key=f"corr_{chave}")

    st.subheader(f"Correções ({len(correcoes)})")
    if correcoes:
        st.dataframe(
            [
                {"Original": c["original"], "Corrigido": c["corrigido"], "Motivo": c["motivo"]}
                for c in correcoes
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.success("Nenhuma correção necessária.")

    if observacoes.strip():
        st.subheader("Observações")
        st.info(observacoes)


st.title("✍️ Corretor de Textos")
st.caption(f"Revisão ortográfica e gramatical preservando o estilo do autor · modelo `{MODELO}`")

aba_corrigir, aba_historico = st.tabs(["Corrigir", "Histórico"])

with aba_corrigir:
    texto = st.text_area("Cole ou digite seu texto", height=250, placeholder="Era uma vez...")

    if st.button("Corrigir texto", type="primary", disabled=not texto.strip()):
        with st.spinner("Revisando o texto..."):
            try:
                resultado = corrigir(texto)
            except ErroCorrecao as e:
                st.error(str(e))
            else:
                registro_id = db.salvar(texto, resultado.texto_corrigido, resultado.correcoes, resultado.observacoes)
                st.session_state["ultimo"] = (
                    f"novo_{registro_id}",
                    texto,
                    resultado.texto_corrigido,
                    resultado.correcoes,
                    resultado.observacoes,
                )

    if "ultimo" in st.session_state:
        st.divider()
        exibir_resultado(*st.session_state["ultimo"])

with aba_historico:
    registros = db.listar()
    if not registros:
        st.write("Nenhuma correção salva ainda.")

    for r in registros:
        previa = r["texto_original"][:80].replace("\n", " ")
        with st.expander(f"{r['data']} · {len(r['correcoes'])} correções · {previa}…"):
            exibir_resultado(f"hist_{r['id']}", r["texto_original"], r["texto_corrigido"], r["correcoes"], r["observacoes"])
            if st.button("Excluir", key=f"excluir_{r['id']}"):
                db.excluir(r["id"])
                st.rerun()
