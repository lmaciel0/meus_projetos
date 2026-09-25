import streamlit as st

import db
from corretor import ErroCorrecao, aplicar, corrigir

st.set_page_config(page_title="Corretor de Textos", page_icon="✍️", layout="wide")
db.inicializar()


def exibir_resultado(registro: dict, editavel: bool) -> None:
    rid, original, correcoes = registro["id"], registro["texto_original"], registro["correcoes"]
    chave = f"{'edit' if editavel else 'hist'}_{rid}"
    automaticas = [c for c in correcoes if c["tipo"] == "automatica"]
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

    if registro["observacoes"].strip():
        st.subheader("Observações de estilo (não aplicadas)")
        st.info(registro["observacoes"])


st.title("✍️ Corretor de Textos")
st.caption("Revisão ortográfica e gramatical preservando o estilo do autor · LanguageTool (offline, gratuito)")

aba_corrigir, aba_historico = st.tabs(["Corrigir", "Histórico"])

with aba_corrigir:
    texto = st.text_area("Cole ou digite seu texto", height=250, placeholder="Era uma vez...")

    # Sem "disabled": o text_area só envia o valor ao perder o foco, então um botão
    # desabilitado engoliria o primeiro clique logo após digitar.
    if st.button("Corrigir texto", type="primary"):
        if not texto.strip():
            st.warning("Digite ou cole um texto para corrigir.")
        else:
            with st.spinner("Revisando o texto... (a primeira correção demora mais: o LanguageTool está iniciando)"):
                try:
                    resultado = corrigir(texto)
                except ErroCorrecao as e:
                    st.error(str(e))
                else:
                    registro_id = db.salvar(texto, resultado.texto_corrigido, resultado.correcoes, resultado.observacoes)
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
        with st.expander(f"{r['data']} · {aceitas} correções · {previa}…"):
            if st.button("Excluir", key=f"excluir_{r['id']}"):
                db.excluir(r["id"])
                st.rerun()
            exibir_resultado(r, editavel=False)
