package com.banco.identificador.controller;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import com.banco.identificador.service.ProcessamentoServiceTest;

@SpringBootTest
@AutoConfigureMockMvc
class ProcessamentoControllerTest {

    @Autowired
    private MockMvc mvc;

    @Test
    void processaArquivosEnviados() throws Exception {
        var file = ProcessamentoServiceTest.arquivo("a.txt", ProcessamentoServiceTest.linha("1234567890", "0001"));

        mvc.perform(multipart("/api/processar").file(file).param("nibs", "1234567890")
                        .header("Origin", "http://localhost:5173"))
                .andExpect(status().isOk())
                .andExpect(header().string("Access-Control-Allow-Origin", "http://localhost:5173"))
                .andExpect(jsonPath("$.arquivos[0]").value("a.txt"))
                .andExpect(jsonPath("$.resultados[0].nib").value("1234567890"))
                .andExpect(jsonPath("$.resultados[0].valores['a.txt']").value("0001"));
    }

    @Test
    void retornaErroSemArquivos() throws Exception {
        mvc.perform(multipart("/api/processar").param("nibs", "1234567890"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.erro").exists());
    }
}
