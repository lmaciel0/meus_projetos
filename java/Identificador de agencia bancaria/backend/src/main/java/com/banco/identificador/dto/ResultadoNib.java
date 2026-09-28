package com.banco.identificador.dto;

import java.util.Map;

/**
 * Valores encontrados para um NIB.
 *
 * @param nib    NIB pesquisado
 * @param valores nome do arquivo → sequência de 4 dígitos (arquivos sem o NIB ficam de fora)
 */
public record ResultadoNib(String nib, Map<String, String> valores) {
}
