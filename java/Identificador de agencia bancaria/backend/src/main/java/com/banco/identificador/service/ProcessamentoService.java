package com.banco.identificador.service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.banco.identificador.dto.RespostaProcessamento;
import com.banco.identificador.dto.ResultadoNib;

/**
 * Cruza arquivos posicionais (largura fixa) procurando NIBs.
 *
 * <p>Layout (colunas base 1): NIB nas colunas 11–20 e sequência alvo nas colunas 49–52.
 * Linhas com menos de 52 caracteres são ignoradas.
 */
@Service
public class ProcessamentoService {

    static final int NIB_INICIO = 10;
    static final int NIB_FIM = 20;
    static final int VALOR_INICIO = 48;
    static final int VALOR_FIM = 52;

    public RespostaProcessamento processar(List<MultipartFile> files, String nibsTexto) throws IOException {
        List<String> nibs = extrairNibs(nibsTexto);
        if (files == null || files.isEmpty()) {
            throw new IllegalArgumentException("Envie ao menos um arquivo .txt.");
        }
        if (nibs.isEmpty()) {
            throw new IllegalArgumentException("Informe ao menos um NIB.");
        }

        Set<String> procurados = new HashSet<>(nibs);
        Map<String, Map<String, String>> valoresPorNib = new LinkedHashMap<>();
        nibs.forEach(nib -> valoresPorNib.put(nib, new LinkedHashMap<>()));

        List<String> arquivos = new ArrayList<>();
        for (MultipartFile file : files) {
            String nome = nomeUnico(file.getOriginalFilename(), arquivos);
            arquivos.add(nome);
            lerArquivo(file, nome, procurados, valoresPorNib);
        }

        List<ResultadoNib> resultados = valoresPorNib.entrySet().stream()
                .map(e -> new ResultadoNib(e.getKey(), e.getValue()))
                .toList();
        return new RespostaProcessamento(arquivos, resultados);
    }

    /** Separa os NIBs por espaço, vírgula, ponto e vírgula ou quebra de linha, sem repetições. */
    static List<String> extrairNibs(String texto) {
        if (texto == null) {
            return List.of();
        }
        Set<String> nibs = new LinkedHashSet<>();
        for (String parte : texto.split("[,;\\s]+")) {
            if (!parte.isBlank()) {
                nibs.add(parte.trim());
            }
        }
        return List.copyOf(nibs);
    }

    /**
     * Lê o arquivo linha a linha, sem carregá-lo inteiro em memória. Usa ISO-8859-1 para que
     * cada byte vire exatamente um caractere e as posições das colunas não se desloquem.
     * Se o NIB aparecer mais de uma vez no mesmo arquivo, vale a primeira ocorrência.
     */
    private void lerArquivo(MultipartFile file, String nome, Set<String> procurados,
                            Map<String, Map<String, String>> valoresPorNib) throws IOException {
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(file.getInputStream(), StandardCharsets.ISO_8859_1))) {
            String linha;
            while ((linha = reader.readLine()) != null) {
                if (linha.length() < VALOR_FIM) {
                    continue;
                }
                String nib = linha.substring(NIB_INICIO, NIB_FIM).trim();
                if (procurados.contains(nib)) {
                    valoresPorNib.get(nib).putIfAbsent(nome, linha.substring(VALOR_INICIO, VALOR_FIM).trim());
                }
            }
        }
    }

    /** Evita colunas duplicadas quando dois arquivos têm o mesmo nome. */
    private static String nomeUnico(String original, List<String> existentes) {
        String base = (original == null || original.isBlank()) ? "arquivo" : original;
        String nome = base;
        for (int i = 2; existentes.contains(nome); i++) {
            nome = base + " (" + i + ")";
        }
        return nome;
    }
}
