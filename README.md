# GoMech AI Service

[![CI](https://github.com/DeyvidJesus/gomech-ai-service-v2/actions/workflows/ci.yml/badge.svg)](https://github.com/DeyvidJesus/gomech-ai-service-v2/actions/workflows/ci.yml)

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
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

O `.env.example` define `ENVIRONMENT=local`. Sem essa variável, o serviço se considera implantado e não sobe com o segredo de serviço padrão, que é público: fora de `local`, `development`, `dev` e `test`, `SERVICE_AUTH_SECRET` precisa ser um valor próprio com pelo menos 32 caracteres.

Verificações (as mesmas da CI):

```bash
ruff check app tests
pytest
```

O provider padrão é `mock`, adequado para desenvolvimento local sem custo externo. `DEFAULT_PROVIDER=gemini` exige `GEMINI_API_KEY`; atualmente apenas `/chat` chama o modelo Gemini e as demais capacidades ainda delegam ao provider mock. O gateway Spring Boot chama este serviço com o segredo de serviço e o contexto do tenant. Em GCP, a chamada também usa identidade IAM do Cloud Run. Os endpoints de capacidade exigem autenticação e contexto do tenant; `/health` e `/docs` ficam disponíveis em `http://localhost:8000`.

## Referências

- [Especificação do serviço](https://github.com/DeyvidJesus/gomech/blob/master/docs/AI_SERVICE_SPECIFICATION.md)
- [ADR-019 — Isolamento do serviço de IA](https://github.com/DeyvidJesus/gomech/blob/master/docs/adr/ADR-019-isolamento-do-servico-de-ia.md)
