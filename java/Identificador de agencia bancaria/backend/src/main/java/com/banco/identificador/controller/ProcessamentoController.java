package com.banco.identificador.controller;

import java.io.IOException;
import java.util.List;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.banco.identificador.dto.RespostaProcessamento;
import com.banco.identificador.service.ProcessamentoService;

@RestController
@RequestMapping("/api")
public class ProcessamentoController {

    private final ProcessamentoService service;

    public ProcessamentoController(ProcessamentoService service) {
        this.service = service;
    }

    @PostMapping(value = "/processar", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public RespostaProcessamento processar(
            @RequestParam("files") List<MultipartFile> files,
            @RequestParam("nibs") String nibs) throws IOException {
        return service.processar(files, nibs);
    }
}
