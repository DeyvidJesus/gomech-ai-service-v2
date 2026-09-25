# GoMech AI Service

Serviço de IA independente em Python e FastAPI. Expõe capacidades automotivas estruturadas por HTTP, aplica autenticação serviço a serviço, guardrails de entrada e uma interface intercambiável para providers. O processo não acessa o banco de dados da plataforma.

## Estrutura

- `app/api/`: rotas e dependências HTTP.
- `app/application/`: coordenação dos casos de uso.
- `app/domain/`: schemas, erros e guardrails.
- `app/infrastructure/providers/`: providers mock, Gemini e OpenAI.
- `app/core/`: configuração, autenticação e observabilidade.

## Executar

Para subir a plataforma completa, use o [guia do ambiente local do repositório principal](https://github.com/DeyvidJesus/gomech/blob/master/docs/guias/ambiente-local.md).

Para executar este serviço isoladamente:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

O provider padrão é `mock`. Para usar outro provider, configure `DEFAULT_PROVIDER` e a respectiva chave de API no ambiente. Os endpoints de capacidade exigem o segredo de serviço e o contexto do tenant; `/health` e `/docs` ficam disponíveis em `http://localhost:8000`.

## Referências

- [Guia de estudo do projeto](https://github.com/DeyvidJesus/gomech/blob/master/docs/guias/guia-de-estudo-entrevista.md)
- [Especificação do serviço](https://github.com/DeyvidJesus/gomech/blob/master/docs/AI_SERVICE_SPECIFICATION.md)
- [ADR-019 — Isolamento do serviço de IA](https://github.com/DeyvidJesus/gomech/blob/master/docs/adr/ADR-019-isolamento-do-servico-de-ia.md)
