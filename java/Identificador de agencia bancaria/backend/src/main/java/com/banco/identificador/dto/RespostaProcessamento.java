package com.banco.identificador.dto;

import java.util.List;

/**
 * Resposta de {@code POST /api/processar}.
 *
 * @param arquivos   nomes dos arquivos na ordem de envio (colunas da tabela)
 * @param resultados uma linha por NIB pesquisado, na ordem informada
 */
public record RespostaProcessamento(List<String> arquivos, List<ResultadoNib> resultados) {
}
