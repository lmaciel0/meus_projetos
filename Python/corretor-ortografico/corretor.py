import json
import os
from dataclasses import dataclass, field

import anthropic
from dotenv import load_dotenv

from prompts import RESPOSTA_SCHEMA, SYSTEM_PROMPT

load_dotenv()

MODELO = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
# Opus 5.5 usa "medium" por padrão; revisão ortográfica se beneficia de mais cuidado.
ESFORCO = os.getenv("CLAUDE_EFFORT", "high")
MAX_TOKENS = 64000


class ErroCorrecao(Exception):
    """Erro com mensagem amigável para exibir na interface."""


@dataclass
class Resultado:
    texto_corrigido: str
    correcoes: list[dict] = field(default_factory=list)
    observacoes: str = ""


_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def corrigir(texto: str) -> Resultado:
    try:
        # Streaming evita timeout HTTP em capítulos longos.
        with _get_client().messages.stream(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            output_config={
                "effort": ESFORCO,
                "format": {"type": "json_schema", "schema": RESPOSTA_SCHEMA},
            },
            messages=[{"role": "user", "content": texto}],
        ) as stream:
            resposta = stream.get_final_message()
    except anthropic.AuthenticationError:
        raise ErroCorrecao("Chave da API inválida. Verifique ANTHROPIC_API_KEY no arquivo .env.")
    except anthropic.PermissionDeniedError:
        raise ErroCorrecao("A chave da API não tem permissão para usar este modelo.")
    except anthropic.NotFoundError:
        raise ErroCorrecao(f"Modelo '{MODELO}' não encontrado.")
    except anthropic.RateLimitError:
        raise ErroCorrecao("Limite de requisições atingido. Aguarde um pouco e tente novamente.")
    except anthropic.BadRequestError as e:
        raise ErroCorrecao(f"Requisição inválida: {e.message}")
    except anthropic.APIStatusError as e:
        raise ErroCorrecao(f"Erro da API ({e.status_code}): {e.message}")
    except anthropic.APIConnectionError:
        raise ErroCorrecao("Falha de conexão com a API. Verifique sua internet.")

    if resposta.stop_reason == "refusal":
        raise ErroCorrecao("O modelo recusou processar este texto.")
    if resposta.stop_reason == "max_tokens":
        raise ErroCorrecao("A resposta foi cortada por ser longa demais. Envie o texto em blocos menores.")

    texto_json = next((b.text for b in resposta.content if b.type == "text"), "")
    try:
        dados = json.loads(texto_json)
    except json.JSONDecodeError:
        raise ErroCorrecao("A resposta do modelo não veio em JSON válido.")

    return Resultado(
        texto_corrigido=dados["texto_corrigido"],
        correcoes=dados["correcoes"],
        observacoes=dados["observacoes"],
    )
