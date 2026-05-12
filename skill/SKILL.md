# Skill — IRPF OCR DEC

## Objetivo

Esta skill auxilia na montagem inicial da Declaração de Imposto de Renda Pessoa Física brasileira a partir de documentos fiscais digitalizados, textos extraídos ou extrações estruturadas.

O objetivo é transformar documentos fiscais em JSON canônico revisável, validado e acompanhado de relatório humano.

No futuro, a skill poderá gerar um arquivo `.DEC` experimental importável no PGD oficial da Receita Federal.

---

## Aviso importante

Esta skill não substitui PGD oficial, contador, revisão humana ou responsabilidade do contribuinte.

---

## Estado atual

Atualmente o projeto possui:

- classificador simples por palavras-chave;
- simulador local de agente individual;
- simulador local de agente em lote;
- pré-triagem de documentos;
- pipeline determinístico de extrações simuladas;
- validação canônica;
- relatório humano;
- testes automatizados.

Ainda não possui OCR real, leitura direta de PDF/imagem, integração final com Agno nem geração `.DEC`.

---

## Fluxos da skill

### Classificador

```text
tests/fixtures/raw_text/
    ↓
tools/classify_document.py
    ↓
document_type provável
```

### Simulador individual

```text
tests/fixtures/raw_text/
    ↓
tools/agent_simulator.py
    ↓
classificação
    ↓
decisão
    ↓
schema recomendado
    ↓
próximo passo
```

### Simulador em lote

```text
tests/fixtures/raw_text/
    ↓
tools/agent_batch_simulator.py
    ↓
decisões por documento
    ↓
recommended_action
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

---

## Comandos

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json

python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json

python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown

python3 tools/preflight_documents.py tests/fixtures/raw_text
python3 tools/preflight_documents.py tests/fixtures/raw_text --json
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown || true
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown --json || true

python3 tools/run_project.py
python3 tools/dev_check.py
```

---

## Decisão recomendada e pré-triagem

O simulador em lote gera `recommended_action`.

A pré-triagem consome essa decisão e produz um status operacional:

```text
ready
blocked
```

Quando `status = ready`, o agente pode avançar para criação de extrações estruturadas JSON.

Quando `status = blocked`, o agente deve interromper o avanço automático e solicitar revisão humana dos documentos bloqueantes.

---

## Documentos suportados atualmente

| Documento | `document_type` | Destino |
|---|---|---|
| Informe de rendimentos PJ | `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| Recibo médico | `recibo_medico` | `pagamentos[]` |
| Plano de saúde | `plano_saude` | `pagamentos[]` |
| Bem imóvel | `bem_imovel` | `bens[]` |
| Bem veículo | `bem_veiculo` | `bens[]` |
