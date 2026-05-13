# IRPF OCR DEC

Projeto experimental para construção de uma skill/agente capaz de auxiliar na montagem inicial da Declaração de Imposto de Renda Pessoa Física a partir de documentos, textos extraídos ou extrações estruturadas.

## Aviso importante

Este projeto não substitui contador, revisão humana, PGD oficial da Receita Federal ou responsabilidade do contribuinte.

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
- limpeza de outputs conhecidos;
- checagem de desenvolvimento integrada;
- testes automatizados.

Ainda não possui OCR real, leitura direta de PDF/imagem, geração `.DEC` ou integração final com Agno.

## Fluxos

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
python3 tools/clean_outputs.py
```

## Limpeza de outputs

Arquivo:

```text
tools/clean_outputs.py
```

Remove os outputs conhecidos gerados pelo projeto:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
outputs/agent-decision.json
outputs/agent-decisions.json
outputs/agent-decisions.report.md
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

O `dev_check.py` chama `clean_outputs.py` antes de executar a pré-triagem, o pipeline principal e os testes.

## Pré-triagem de documentos

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

Quando `ready`, o fluxo pode avançar para criação das extrações estruturadas JSON.

Quando `blocked`, o fluxo deve parar até revisão humana ou classificação manual dos documentos bloqueantes.

## Git e versionamento

Fluxo recomendado:

```bash
git status
python3 tools/dev_check.py
git add .
git commit -m "Mensagem objetiva do que mudou"
git push
```

## Limitações atuais

O projeto ainda não possui OCR real, leitura de PDF/imagem, classificação robusta de documentos reais, geração de `.DEC`, transmissão da declaração, parser reverso `.DEC`, suporte a dependentes, suporte a investimentos ou cálculo completo de imposto.
