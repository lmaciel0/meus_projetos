from analise import REGRA_NOME, REGRA_REPETICAO, estatisticas, nomes_parecidos, repeticoes
from diferencas import destacar


def test_repeticao_proxima_e_apontada_na_segunda_ocorrencia():
    texto = "Ela olhou a janela e olhou de novo."
    [o] = repeticoes(texto)
    assert (o["trecho"], o["offset"], o["regra"]) == ("olhou", texto.rindex("olhou"), REGRA_REPETICAO)


def test_repeticao_ignora_palavras_comuns_nomes_e_dicionario():
    assert repeticoes("Ela estava ali, estava mesmo.") == []
    assert repeticoes("Aelin correu. Aelin parou.") == []
    assert repeticoes("o grifo voou e o grifo pousou", ignoradas={"grifo"}) == []


def test_repeticao_distante_nao_conta():
    texto = "olhou " + "um " * 20 + "olhou"
    assert repeticoes(texto) == []


def test_nome_com_uma_letra_diferente_e_apontado():
    texto = "Então Aelin sorriu. Depois Aelin correu. Mais tarde Aelyn voltou."
    [o] = nomes_parecidos(texto)
    assert (o["trecho"], o["sugestao"], o["regra"]) == ("Aelyn", "Aelin", REGRA_NOME)
    assert o["offset"] == texto.index("Aelyn")


def test_nome_do_dicionario_vale_como_referencia():
    [o] = nomes_parecidos("Rowen chegou.", ignoradas={"rowan"})
    assert o["sugestao"] == "Rowan"


def test_palavra_comum_no_inicio_da_frase_nao_vira_nome():
    assert nomes_parecidos("Estava frio. Estava escuro. Estavam sós.") == []


def test_estatisticas():
    e = estatisticas("A noite caiu.\n\nA noite passou e ela estava lá.")
    assert e["palavras"] == 10
    assert e["paragrafos"] == 2
    assert e["mais_usadas"][0] == ("noite", 2)
    assert "estava" not in dict(e["mais_usadas"])


def test_destaque_mostra_o_que_saiu_e_o_que_entrou():
    html = destacar("Ele nao sabia <nada>.", "Ele não sabia <nada>.")
    assert "<del>nao</del><ins>não</ins>" in html
    assert "&lt;nada&gt;" in html


def test_nome_so_no_inicio_de_frase_vale_se_o_corretor_nao_conhece():
    texto = "Aelin olhou. Aelin saiu. Aelyn voltou. Estava frio. Estava. Estavam."
    desconhecidas = {"Aelin", "Aelyn"}
    [o] = nomes_parecidos(texto, desconhecidas=desconhecidas)
    assert (o["trecho"], o["sugestao"]) == ("Aelyn", "Aelin")
