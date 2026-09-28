package com.banco.identificador.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;

import com.banco.identificador.dto.RespostaProcessamento;

public class ProcessamentoServiceTest {

    private final ProcessamentoService service = new ProcessamentoService();

    /** Monta uma linha posicional com o NIB nas colunas 11–20 e o valor nas colunas 49–52. */
    public static String linha(String nib, String valor) {
        return "X".repeat(10) + nib + " ".repeat(28) + valor + "FIM";
    }

    public static MockMultipartFile arquivo(String nome, String... linhas) {
        return new MockMultipartFile("files", nome, "text/plain",
                String.join("\n", linhas).getBytes(StandardCharsets.ISO_8859_1));
    }

    @Test
    void cruzaNibsEntreArquivos() throws Exception {
        var a = arquivo("a.txt", linha("1234567890", "0001"), linha("1111111111", "0456"));
        var b = arquivo("b.txt", linha("1234567890", "0002"));

        RespostaProcessamento resposta = service.processar(List.of(a, b), "1234567890, 1111111111\n9999999999");

        assertThat(resposta.arquivos()).containsExactly("a.txt", "b.txt");
        assertThat(resposta.resultados()).hasSize(3);
        assertThat(resposta.resultados().get(0).valores()).isEqualTo(Map.of("a.txt", "0001", "b.txt", "0002"));
        assertThat(resposta.resultados().get(1).valores()).isEqualTo(Map.of("a.txt", "0456"));
        assertThat(resposta.resultados().get(2).valores()).isEmpty();
    }

    @Test
    void ignoraLinhasCurtasEMantemPrimeiraOcorrencia() throws Exception {
        var a = arquivo("a.txt", "curta", linha("1234567890", "0001"), linha("1234567890", "0009"));

        var resposta = service.processar(List.of(a), "1234567890");

        assertThat(resposta.resultados().get(0).valores()).containsEntry("a.txt", "0001");
    }

    @Test
    void renomeiaArquivosComNomeRepetido() throws Exception {
        var a = arquivo("dados.txt", linha("1234567890", "0001"));
        var b = arquivo("dados.txt", linha("1234567890", "0002"));

        var resposta = service.processar(List.of(a, b), "1234567890");

        assertThat(resposta.arquivos()).containsExactly("dados.txt", "dados.txt (2)");
        assertThat(resposta.resultados().get(0).valores()).containsEntry("dados.txt (2)", "0002");
    }

    @Test
    void extraiNibsSemRepeticao() {
        assertThat(ProcessamentoService.extrairNibs(" 1, 2;3\r\n2  4 ")).containsExactly("1", "2", "3", "4");
    }

    @Test
    void exigeNibs() {
        var a = arquivo("a.txt", linha("1234567890", "0001"));
        assertThatThrownBy(() -> service.processar(List.of(a), "  "))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("NIB");
    }
}
