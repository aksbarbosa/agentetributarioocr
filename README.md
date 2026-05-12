# IRPF OCR DEC

Projeto experimental para montar uma base de agente/skill para organizar dados de IRPF a partir de documentos, textos extraídos ou extrações estruturadas.

## Aviso importante

Este projeto não substitui contador, PGD oficial, revisão humana ou responsabilidade do contribuinte.

Fluxo correto:

```text
documento
    ↓
OCR ou texto extraído
    ↓
classificação
    ↓
pré-triagem
    ↓
extração estruturada
    ↓
JSON canônico
    ↓
validação
    ↓
relatório humano
    ↓
revisão
    ↓
geração futura do .DEC
```

## Estado atual

O projeto possui:

- classificador simples;
- simulador local individual;
- simulador local em lote;
- pré-triagem de documentos;
- pipeline para extrações simuladas;
- validação canônica;
- relatório humano;
- checagem de desenvolvimento integrada;
- testes automatizados.

Ainda não possui OCR real, leitura direta de PDF/imagem, geração `.DEC` ou integração final com Agno.

## Fluxos

### Classificador

```text
tests/fixtures/raw_text/
    ↓
tools/classify_document.py
    ↓
document_type provável
```

### Simulador em lote

```text
tests/fixtures/raw_text/
    ↓
tools/agent_batch_simulator.py
    ↓
summary + recommended_action + decisions
    ↓
outputs/agent-decisions.json
    ↓
outputs/agent-decisions.report.md
```

### Pré-triagem

```text
tests/fixtures/raw_text/
    ↓
tools/preflight_documents.py
    ↓
agent_batch_simulator.py
    ↓
status ready ou blocked
    ↓
outputs/preflight-documents.json
    ↓
outputs/preflight-documents.report.md
```

### Checagem de desenvolvimento

```text
tools/dev_check.py
    ↓
Validar configuração
    ↓
Limpar outputs
    ↓
Rodar pré-triagem de documentos
    ↓
Rodar projeto
    ↓
Rodar testes
```

## Comandos principais

```bash
python3 tools/run_project.py
python3 tests/run_tests.py
python3 tools/dev_check.py
```

Classificador:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Simulador individual:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

Simulador em lote:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown
```

Pré-triagem:

```bash
python3 tools/preflight_documents.py tests/fixtures/raw_text
python3 tools/preflight_documents.py tests/fixtures/raw_text --json
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown || true
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown --json || true
```

## Pré-triagem

Arquivo:

```text
tools/preflight_documents.py
```

Saídas:

```text
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

Status possíveis:

```text
ready
blocked
```

Quando `ready`, o fluxo pode avançar para criação de extrações estruturadas JSON.

Quando `blocked`, o fluxo deve parar até revisão humana ou classificação manual dos documentos bloqueantes.

## dev_check

Arquivo:

```text
tools/dev_check.py
```

Agora executa:

```text
1. Validar configuração
2. Limpar outputs
3. Rodar pré-triagem de documentos
4. Rodar projeto
5. Rodar testes
```

A pré-triagem do `dev_check.py` usa somente o cenário positivo:

```bash
python3 tools/preflight_documents.py tests/fixtures/raw_text
```

O cenário bloqueado retorna exit code `1` de propósito e fica coberto pelos testes automatizados.
