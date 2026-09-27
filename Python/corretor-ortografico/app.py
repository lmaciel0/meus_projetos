import json
import math
import time
from pathlib import Path

import pandas as pd
import streamlit as st

import analise
import db
import docx_io
import ia
from corretor import (
    MOTIVO_DIALOGO,
    MOTIVO_FIXA,
    ErroCorrecao,
    aplicar,
    correcao_de_observacao,
    corrigir,
    sobrepoe,
)
from diferencas import destacar
from pdf import extrair_texto as extrair_pdf

POR_PAGINA = 10
ROTULOS_OBSERVACAO = {"estilo": "Estilo", "repeticao": "Repetição", "consistencia": "Nome", "outra": "Outro"}
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

st.set_page_config(page_title="Corretor de Textos", page_icon="✍️", layout="wide")
db.inicializar()


@st.cache_data(show_spinner=False, max_entries=50)
def _docx(texto: str, original: bytes | None) -> tuple[bytes, bool]:
    return docx_io.gerar(texto, original)


def _salvar(registro: dict) -> None:
    """Grava as decisões do autor e refaz o texto corrigido a partir delas."""
    if all("offset" in c for c in registro["correcoes"]):
        registro["texto_corrigido"] = aplicar(registro["texto_original"], registro["correcoes"])
    # Registros da versão anterior (sem offsets) mantêm o texto salvo.
    db.atualizar(registro["id"], registro["texto_corrigido"], registro["correcoes"], registro["observacoes"])


def _exibir_automaticas(registro: dict, editavel: bool, travado: bool) -> bool:
    rid, correcoes = registro["id"], registro["correcoes"]
    automaticas = [c for c in correcoes if c["tipo"] == "automatica"]
    # Preenchido no fim: a contagem depende do que foi desmarcado na tabela.
    titulo = st.empty()
    titulo.subheader(f"Correções aplicadas ({sum(c['aceita'] for c in automaticas)} de {len(automaticas)})")
    if not automaticas:
        st.success("Nenhuma correção ortográfica necessária.")
        return False

    tabela = pd.DataFrame(
        {
            "Aplicar": [c["aceita"] for c in automaticas],
            "Original": [c["original"] for c in automaticas],
            "Corrigido": [c["corrigido"] for c in automaticas],
            "Motivo": [c["motivo"] for c in automaticas],
        }
    )
    if not editavel:
        st.dataframe(tabela, width="stretch", hide_index=True)
        return False

    st.caption("Desmarque em **Aplicar** para desfazer uma correção só neste texto.")
    # A chave muda com as decisões salvas: o editor recomeça do estado do banco.
    estado = tuple((c.get("offset"), c["aceita"]) for c in automaticas)
    editada = st.data_editor(
        tabela,
        column_config={"Aplicar": st.column_config.CheckboxColumn("Aplicar", width="small")},
        disabled=True if travado else ["Original", "Corrigido", "Motivo"],
        width="stretch",
        hide_index=True,
        key=f"auto_{rid}_{hash(estado)}",
    )
    mudou = False
    for c, aplicar_ in zip(automaticas, editada["Aplicar"]):
        if bool(aplicar_) != c["aceita"]:
            c["aceita"], mudou = bool(aplicar_), True
    titulo.subheader(f"Correções aplicadas ({sum(c['aceita'] for c in automaticas)} de {len(automaticas)})")

    palavras = sorted({c["original"] for c in automaticas if c["motivo"] not in (MOTIVO_FIXA, MOTIVO_DIALOGO)})
    if palavras and not travado:
        with st.expander("Alguma dessas palavras está certa sempre? (nomes, gírias, termos da história)"):
            escolhidas = st.multiselect(
                "Não corrigir mais",
                palavras,
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
                _salvar(registro)
                st.rerun()
    return mudou


def _exibir_sugestoes(registro: dict, editavel: bool, travado: bool) -> bool:
    rid = registro["id"]
    sugestoes = [c for c in registro["correcoes"] if c["tipo"] == "sugestao"]
    if not sugestoes:
        return False
    st.subheader(f"Sugestões para conferir ({len(sugestoes)})")
    if not editavel:
        st.dataframe(
            [
                {
                    "Status": "✅ aceita" if c["aceita"] else "❌ recusada",
                    "Original": c["original"],
                    "Sugestão": " / ".join(c["opcoes"]) if c.get("opcoes") and not c["aceita"] else c["corrigido"],
                    "Motivo": c["motivo"],
                }
                for c in sugestoes
            ],
            width="stretch",
            hide_index=True,
        )
        return False

    st.caption("Não são aplicadas automaticamente. Marque ou escolha as que quiser aceitar.")
    if not travado:
        col_todas, col_nenhuma, _ = st.columns([1, 1, 3])
        for coluna, rotulo, valor in ((col_todas, "Aceitar todas", True), (col_nenhuma, "Recusar todas", False)):
            if coluna.button(rotulo, key=f"sug_todas_{rid}_{valor}"):
                for c in sugestoes:
                    c["aceita"] = valor
                _salvar(registro)
                st.rerun()
    mudou = False
    for c in sugestoes:
        # Chave pelo trecho e pela decisão salva, não pela posição: aplicar uma observação
        # muda a lista, e "Aceitar todas" muda o valor sem passar pelo checkbox.
        chave = f"sug_{rid}_{c.get('offset')}_{c['original']}_{c['aceita']}"
        contexto = f" — em “{c['contexto']}”" if c.get("contexto") else ""
        if c.get("opcoes"):
            manter = f"manter “{c['original']}”"
            opcoes = [manter, *c["opcoes"]]
            escolha = st.radio(
                f"“{c['original']}” — {c['motivo']}{contexto}",
                opcoes,
                index=opcoes.index(c["corrigido"]) if c["aceita"] else 0,
                horizontal=True,
                disabled=travado,
                key=chave,
            )
            aceita = escolha != manter
            corrigido = escolha if aceita else c["corrigido"]
            mudou |= aceita != c["aceita"] or corrigido != c["corrigido"]
            c["aceita"], c["corrigido"] = aceita, corrigido
            continue
        aceita = st.checkbox(
            f"“{c['original']}” → “{c['corrigido']}” — {c['motivo']}{contexto}",
            value=c["aceita"],
            disabled=travado,
            key=f"{chave}_{c['corrigido']}",
        )
        mudou |= aceita != c["aceita"]
        c["aceita"] = aceita
    return mudou


def _texto_observacao(o: dict) -> str:
    rotulo = ROTULOS_OBSERVACAO.get(o.get("tipo"), "Outro")
    trecho = f"“{o['trecho']}”: " if o.get("trecho") else ""
    sugestao = f" (sugestão: “{o['sugestao']}”)" if o.get("sugestao") else ""
    return f"**{rotulo}** · {trecho}{o['mensagem']}{sugestao}"


def _exibir_observacoes(registro: dict, editavel: bool, travado: bool) -> None:
    rid, observacoes = registro["id"], registro["observacoes"]
    visiveis = [(i, o) for i, o in enumerate(observacoes) if not o.get("dispensada")]
    if not visiveis:
        return
    st.subheader(f"Observações ({len(visiveis)})")
    if not editavel:
        st.markdown("\n".join(f"- {_texto_observacao(o)}" for _, o in visiveis))
        return

    st.caption(
        "Estilo, repetições e nomes escritos de jeitos diferentes. Nada aqui é aplicado sozinho."
        " **Silenciar** esconde este tipo de aviso nas próximas correções (dá para desfazer no Dicionário)."
    )
    with st.container(height=420 if len(visiveis) > 8 else "content"):
        for i, o in visiveis:
            col_texto, col_aplicar, col_dispensar, col_silenciar = st.columns([8, 1.3, 1.5, 1.4])
            col_texto.markdown(_texto_observacao(o))
            pode_aplicar = (
                not travado and o.get("sugestao") and "offset" in o and not sobrepoe(o, registro["correcoes"])
            )
            if col_aplicar.button("Aplicar", key=f"obs_apl_{rid}_{i}", disabled=not pode_aplicar):
                # Sugestões não aceitas no mesmo trecho saem: aplicadas juntas, estragariam o texto.
                registro["correcoes"] = sorted(
                    [c for c in registro["correcoes"] if not sobrepoe(o, [{**c, "aceita": True}])]
                    + [correcao_de_observacao(o)],
                    key=lambda c: c.get("offset", 0),
                )
                o["dispensada"] = True
                _salvar(registro)
                st.rerun()
            if col_dispensar.button("Dispensar", key=f"obs_dis_{rid}_{i}"):
                o["dispensada"] = True
                _salvar(registro)
                st.rerun()
            if col_silenciar.button("Silenciar", key=f"obs_sil_{rid}_{i}", disabled=not o.get("regra")):
                db.adicionar_regra(o["regra"], o["mensagem"])
                for outra in observacoes:
                    if outra.get("regra") == o["regra"]:
                        outra["dispensada"] = True
                _salvar(registro)
                st.rerun()


def _exibir_textos(registro: dict, editavel: bool, chave: str) -> None:
    rid, original = registro["id"], registro["texto_original"]
    final = registro["texto_final"] or registro["texto_corrigido"]

    aba_lado, aba_diferencas = st.tabs(["Lado a lado", "Alterações destacadas"])
    with aba_lado:
        col_orig, col_corr = st.columns(2)
        with col_orig:
            st.markdown("**Original**")
            st.text_area("Original", original, height=400, disabled=True, label_visibility="collapsed", key=f"orig_{chave}")
        with col_corr:
            st.markdown("**Corrigido**" + (" (editado à mão)" if registro["texto_final"] else ""))
            # A chave muda junto com o texto para o campo refletir cada decisão salva.
            editado = st.text_area(
                "Corrigido",
                final,
                height=400,
                disabled=not editavel,
                label_visibility="collapsed",
                key=f"corr_{chave}_{hash(final)}",
            )
            if editavel:
                col_salvar, col_descartar = st.columns(2)
                # Sem "disabled": o text_area só envia o valor ao perder o foco, e um botão
                # desabilitado engoliria o primeiro clique logo depois de digitar.
                if col_salvar.button("Salvar edição", key=f"salvar_ed_{rid}"):
                    if editado == final:
                        st.toast("Nada mudou no texto.")
                    else:
                        db.salvar_edicao(rid, "" if editado == registro["texto_corrigido"] else editado)
                        st.rerun()
                if registro["texto_final"] and col_descartar.button("Descartar edição", key=f"descartar_ed_{rid}"):
                    db.salvar_edicao(rid, "")
                    st.rerun()
    with aba_diferencas:
        with st.container(height=440):
            st.html(destacar(original, final))

    nome = Path(registro["arquivo"]).stem if registro["arquivo"] else "texto"
    dados_docx, preservada = _docx(final, registro["arquivo_dados"])
    col_txt, col_docx = st.columns(2)
    col_txt.download_button(
        "Baixar texto corrigido (.txt)",
        final,
        file_name=f"{nome}_corrigido.txt",
        mime="text/plain",
        on_click="ignore",
        key=f"baixar_txt_{chave}",
    )
    col_docx.download_button(
        "Baixar no Word (.docx)",
        dados_docx,
        file_name=f"{nome}_corrigido.docx",
        mime=MIME_DOCX,
        on_click="ignore",
        key=f"baixar_docx_{chave}",
        help=(
            "Mantém a formatação do documento enviado."
            if preservada
            else "Documento simples, um parágrafo por linha."
            + (" A edição manual mudou os parágrafos, então a formatação original não pôde ser mantida." if registro["arquivo_dados"] else "")
        ),
    )


def exibir_resultado(registro: dict, editavel: bool) -> None:
    chave = f"{'edit' if editavel else 'hist'}_{registro['id']}"
    # Com edição manual salva, as decisões ficam travadas: mudá-las apagaria a edição.
    travado = bool(registro["texto_final"])

    # Os textos ficam no topo, mas dependem das decisões renderizadas abaixo.
    area_textos = st.container()
    if travado and editavel:
        st.info("O texto foi editado à mão. Para mudar as correções, descarte a edição (acima, em “Lado a lado”).")

    mudou = _exibir_automaticas(registro, editavel, travado)
    mudou |= _exibir_sugestoes(registro, editavel, travado)
    if mudou:
        _salvar(registro)
    _exibir_observacoes(registro, editavel, travado)

    with st.expander("Estatísticas do texto"):
        texto = registro["texto_final"] or registro["texto_corrigido"]
        estatisticas = analise.estatisticas(texto, set(db.listar_ignoradas()))
        col_palavras, col_paragrafos = st.columns(2)
        col_palavras.metric("Palavras", estatisticas["palavras"])
        col_paragrafos.metric("Parágrafos", estatisticas["paragrafos"])
        if estatisticas["mais_usadas"]:
            st.markdown("**Palavras que você mais usou** (sem artigos, preposições e afins)")
            st.dataframe(
                pd.DataFrame(estatisticas["mais_usadas"], columns=["Palavra", "Vezes"]), hide_index=True, width="content"
            )

    with area_textos:
        _exibir_textos(registro, editavel, chave)


st.title("✍️ Corretor de Textos")
st.caption("Revisão ortográfica e gramatical preservando o estilo do autor · LanguageTool ou IA local (offline, gratuito)")

aba_corrigir, aba_historico, aba_dicionario, aba_backup = st.tabs(["Corrigir", "Histórico", "Dicionário", "Backup"])

with aba_corrigir:
    modo = st.radio("Entrada", ["Colar texto", "Enviar arquivo"], horizontal=True, label_visibility="collapsed")
    if modo == "Colar texto":
        texto = st.text_area("Cole ou digite seu texto", height=250, placeholder="Era uma vez...")
    else:
        enviado = st.file_uploader(
            "Envie um arquivo do Word (.docx) ou PDF. No Word, a formatação é mantida no arquivo corrigido.",
            type=["docx", "pdf"],
        )

    ia_ok, ia_situacao = ia.disponivel()
    motor = st.radio(
        "Revisar com",
        ["LanguageTool (rápido)", "IA local – Gemma 4 (lenta, corrige mais)"],
        horizontal=True,
        help="A IA pega mais erros, mas leva cerca de 1 minuto a cada 75 palavras neste computador."
        " Tudo o que ela muda vira sugestão para você conferir.",
    )
    usar_ia = motor.startswith("IA")
    if usar_ia and not ia_ok:
        st.warning(ia_situacao)
    elif usar_ia and modo == "Colar texto" and texto.strip():
        st.caption(
            f"Estimativa: cerca de {ia.estimativa_minutos(texto)} min. Se interromper, os parágrafos já"
            " revisados são aproveitados na próxima vez."
        )

    # Sem "disabled": o text_area só envia o valor ao perder o foco, então um botão
    # desabilitado engoliria o primeiro clique logo após digitar.
    if st.button("Corrigir texto", type="primary"):
        if modo == "Enviar arquivo" and enviado is None:
            st.warning("Envie um arquivo para corrigir.")
        elif modo == "Colar texto" and not texto.strip():
            st.warning("Digite ou cole um texto para corrigir.")
        elif usar_ia and not ia_ok:
            st.warning(ia_situacao)
        else:
            barra = st.progress(0.0, text="Preparando...")
            comeco = time.time()

            def progresso(feitos: int, total: int) -> None:
                restante = (time.time() - comeco) / feitos * (total - feitos)
                previsao = f" · falta cerca de {math.ceil(restante / 60)} min" if usar_ia and feitos < total else ""
                barra.progress(feitos / total, text=f"Revisando o texto... parte {feitos} de {total}{previsao}")

            aviso = (
                "Revisando com a IA... (deixe esta aba aberta)"
                if usar_ia
                else "Revisando... (a primeira correção demora mais: o LanguageTool está iniciando)"
            )
            with st.spinner(aviso):
                arquivo, arquivo_dados = "", None
                try:
                    if modo == "Enviar arquivo":
                        arquivo = enviado.name
                        if arquivo.lower().endswith(".docx"):
                            arquivo_dados = enviado.getvalue()
                            texto = docx_io.extrair_texto(arquivo_dados)
                        else:
                            texto = extrair_pdf(enviado.getvalue())
                    dicionario = (set(db.listar_ignoradas()), db.listar_fixas(), set(db.listar_regras()))
                    if usar_ia:
                        resultado, falhas = ia.corrigir_com_ia(texto, *dicionario, progresso, cache=db)
                        if falhas:
                            st.warning(
                                f"A IA não devolveu uma revisão aproveitável em {falhas} parágrafo(s);"
                                " eles ficaram sem sugestões."
                            )
                    else:
                        resultado = corrigir(texto, *dicionario, progresso)
                except ErroCorrecao as e:
                    st.error(str(e))
                else:
                    st.session_state["ultimo_id"] = db.salvar(
                        texto,
                        resultado.texto_corrigido,
                        resultado.correcoes,
                        resultado.observacoes,
                        arquivo,
                        arquivo_dados,
                    )
            barra.empty()

    ultimo = db.obter(st.session_state["ultimo_id"]) if "ultimo_id" in st.session_state else None
    if ultimo:
        st.divider()
        exibir_resultado(ultimo, editavel=True)

with aba_historico:
    busca = st.text_input("Buscar", placeholder="nome do arquivo, trecho do texto ou data (ex.: 2026-09)")
    total = db.contar(busca)
    if not total:
        st.write("Nada encontrado." if busca.strip() else "Nenhuma correção salva ainda.")
    paginas = max(1, math.ceil(total / POR_PAGINA))
    pagina = st.number_input(f"Página (de {paginas})", 1, paginas, 1) if paginas > 1 else 1

    for r in db.listar(busca, POR_PAGINA, (pagina - 1) * POR_PAGINA):
        previa = r["texto_original"][:80].replace("\n", " ")
        aceitas = sum(c["aceita"] for c in r["correcoes"])
        origem = f"📄 {r['arquivo']} · " if r["arquivo"] else ""
        with st.expander(f"{r['data']} · {origem}{aceitas} correções · {previa}…"):
            confirmar = f"confirmar_excluir_{r['id']}"
            if st.session_state.get(confirmar):
                st.warning("Excluir esta correção do histórico? Não dá para desfazer.")
                col_sim, col_nao = st.columns(2)
                if col_sim.button("Sim, excluir", type="primary", key=f"sim_{r['id']}"):
                    db.excluir(r["id"])
                    del st.session_state[confirmar]
                    st.rerun()
                if col_nao.button("Cancelar", key=f"nao_{r['id']}"):
                    del st.session_state[confirmar]
                    st.rerun()
            elif st.button("Excluir", key=f"excluir_{r['id']}"):
                st.session_state[confirmar] = True
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

        aprendidas = db.sugestoes_de_fixas()
        if aprendidas:
            st.markdown("**Sugeridas pelo seu histórico**")
            st.caption("Correções que você já aceitou várias vezes. Vire fixa para não depender do LanguageTool.")
            for original, corrigido, vezes in aprendidas:
                col_regra, col_adicionar = st.columns([5, 1])
                col_regra.write(f"{original} → {corrigido} ({vezes} vezes)")
                if col_adicionar.button("Tornar fixa", key=f"aprender_{original}_{corrigido}"):
                    db.adicionar_fixa(original, corrigido)
                    st.rerun()

    st.subheader("Avisos silenciados")
    regras = db.listar_regras()
    if not regras:
        st.caption("Nenhum. Use **Silenciar** numa observação para parar de ver aquele tipo de aviso.")
    for regra, descricao in regras.items():
        col_regra, col_remover = st.columns([5, 1])
        col_regra.markdown(f"`{regra}` — {descricao}")
        if col_remover.button("Reativar", key=f"rem_regra_{regra}"):
            db.remover_regra(regra)
            st.rerun()

with aba_backup:
    st.caption("Guarde o dicionário pessoal e o histórico num arquivo, para não perder ou levar a outro computador.")
    st.download_button(
        "Baixar backup (.json)",
        lambda: json.dumps(db.exportar(), ensure_ascii=False, indent=2),
        file_name="corretor_backup.json",
        mime="application/json",
        on_click="ignore",
        help="Os arquivos .docx enviados não entram no backup, só os textos.",
    )
    st.divider()
    backup = st.file_uploader("Restaurar backup", type="json", help="Junta ao que já existe; nada é apagado.")
    if backup is not None and st.button("Restaurar"):
        try:
            contagem = db.importar(json.loads(backup.getvalue().decode("utf-8")))
        except (ValueError, KeyError, TypeError) as e:
            st.error(f"Não foi possível restaurar: {e}")
        else:
            st.success(
                f"Restaurado: {contagem['palavras_aceitas']} palavras aceitas, {contagem['correcoes_fixas']}"
                f" correções fixas, {contagem['regras_desligadas']} avisos silenciados e"
                f" {contagem['historico']} textos novos no histórico."
            )
