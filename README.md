# IRPF OCR DEC

Projeto experimental para construção de uma skill/agente capaz de auxiliar na montagem inicial da Declaração de Imposto de Renda Pessoa Física a partir de documentos digitalizados, textos extraídos ou extrações estruturadas.

A ideia central é transformar documentos fiscais em um JSON canônico revisável e, futuramente, gerar um arquivo `.DEC` experimental importável no PGD oficial da Receita Federal.

---

## Aviso importante

Este projeto não substitui contador, revisão humana, PGD oficial da Receita Federal ou responsabilidade do contribuinte.

O fluxo correto é:

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

---

## Estado atual do projeto

Nesta fase, o projeto ainda **não faz OCR real** e ainda **não gera `.DEC`**.

Atualmente ele possui:

1. classificador simples de documentos;
2. simulador local de agente individual;
3. simulador local de agente em lote;
4. ferramenta de pré-triagem de documentos;
5. pipeline principal para extrações simuladas em JSON;
6. validação canônica;
7. relatório humano;
8. testes automatizados.

---

## Fluxos atuais

### Classificador

```text
tests/fixtures/raw_text/
    ↓
tools/classify_document.py
    ↓
document_type provável
```

### Simulador local individual

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

### Simulador local em lote

```text
tests/fixtures/raw_text/
    ↓
tools/agent_batch_simulator.py
    ↓
classificação de cada documento
    ↓
decisão individual por documento
    ↓
recommended_action
    ↓
outputs/agent-decisions.json
    ↓
outputs/agent-decisions.report.md
```

### Pré-triagem de documentos

```text
tests/fixtures/raw_text/
    ↓
tools/preflight_documents.py
    ↓
agent_batch_simulator.py
    ↓
summary + recommended_action + decisions
    ↓
status ready ou blocked
    ↓
outputs/preflight-documents.json
    ↓
outputs/preflight-documents.report.md
```

### Pipeline principal

```text
inputs/extracted/
    ↓
tools/run_project.py
    ↓
validação das extrações
    ↓
normalização
    ↓
JSON canônico consolidado
    ↓
validação canônica
    ↓
relatório humano
```

---

## Documentos suportados atualmente

| Documento | `document_type` | Destino |
|---|---|---|
| Informe de rendimentos PJ | `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| Recibo médico | `recibo_medico` | `pagamentos[]` |
| Plano de saúde | `plano_saude` | `pagamentos[]` |
| Bem imóvel | `bem_imovel` | `bens[]` |
| Bem veículo | `bem_veiculo` | `bens[]` |

---

## Pastas principais

```text
inputs/raw/
inputs/extracted/
outputs/
tests/fixtures/raw_text/
tests/fixtures/raw_text_with_unknown/
skill/
tools/
```

### `tests/fixtures/raw_text/`

Contém textos brutos simulados com documentos conhecidos.

### `tests/fixtures/raw_text_with_unknown/`

Contém os mesmos textos conhecidos mais:

```text
documento_desconhecido.txt
```

Essa pasta testa o comportamento do simulador em lote e da pré-triagem quando há um documento que exige revisão manual.

---

## Comandos principais

Rodar projeto:

```bash
python3 tools/run_project.py
```

Rodar testes:

```bash
python3 tests/run_tests.py
```

Rodar checagem completa:

```bash
python3 tools/dev_check.py
```

Classificar texto bruto:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Simular agente individual:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

Simular agente em lote:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown
```

Rodar pré-triagem com todos os documentos conhecidos:

```bash
python3 tools/preflight_documents.py tests/fixtures/raw_text
```

Rodar pré-triagem com documento desconhecido:

```bash
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown || true
```

Rodar pré-triagem com JSON no terminal:

```bash
python3 tools/preflight_documents.py tests/fixtures/raw_text --json
python3 tools/preflight_documents.py tests/fixtures/raw_text_with_unknown --json || true
```

---

## Pré-triagem de documentos

Arquivo principal:

```text
tools/preflight_documents.py
```

A pré-triagem usa o simulador em lote para decidir se o fluxo pode avançar.

Ela gera:

```text
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

Formato resumido do JSON:

```json
{
  "input_dir": "tests/fixtures/raw_text_with_unknown",
  "status": "blocked",
  "can_continue": false,
  "message": "Há 1 documento(s) que exigem revisão manual antes de avançar para extração estruturada.",
  "next_step": "Revisar manualmente os documentos marcados antes de continuar.",
  "summary": {},
  "blocking_documents": [],
  "batch_response": {}
}
```

Status possíveis:

```text
ready
blocked
```

Quando `status = ready`, o fluxo pode avançar para criação das extrações estruturadas JSON.

Quando `status = blocked`, o fluxo deve parar até revisão humana ou classificação manual dos documentos bloqueantes.

O relatório Markdown da pré-triagem possui:

```markdown
# Relatório de pré-triagem de documentos

## Mensagem
## Próximo passo
## Resumo
## Documentos bloqueantes
## Decisão operacional
```

---

## Git e versionamento

Fluxo recomendado:

```bash
git status
python3 tools/dev_check.py
git add .
git commit -m "Mensagem objetiva do que mudou"
git push
```

---

## Limitações atuais

O projeto ainda não possui OCR real, leitura de PDF/imagem, classificação robusta de documentos reais, geração de `.DEC`, transmissão da declaração, parser reverso `.DEC`, suporte a dependentes, suporte a investimentos ou cálculo completo de imposto.
