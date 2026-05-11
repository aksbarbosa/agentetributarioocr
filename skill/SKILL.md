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
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown

python3 tools/run_project.py
python3 tools/dev_check.py
```

---

## Decisão recomendada do simulador em lote

O simulador em lote gera `recommended_action`.

Quando todos os documentos podem continuar:

```json
{
  "recommended_action": {
    "can_continue": true,
    "message": "Todos os 5 documento(s) foram classificados com confiança suficiente para continuar.",
    "next_step": "Prosseguir para criação das extrações estruturadas JSON."
  }
}
```

Quando há documentos exigindo revisão manual:

```json
{
  "recommended_action": {
    "can_continue": false,
    "message": "Há 1 documento(s) que exigem revisão manual antes de avançar para extração estruturada.",
    "next_step": "Revisar manualmente os documentos marcados antes de continuar."
  }
}
```

O relatório Markdown também possui:

```markdown
## Ação recomendada
## Status dos documentos
### Aptos a continuar
### Exigem revisão
## Documentos que exigem revisão manual
```

Essas seções permitem separar rapidamente documentos classificados com confiança suficiente daqueles que exigem revisão humana.

---

## Documentos suportados atualmente

| Documento | `document_type` | Destino |
|---|---|---|
| Informe de rendimentos PJ | `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| Recibo médico | `recibo_medico` | `pagamentos[]` |
| Plano de saúde | `plano_saude` | `pagamentos[]` |
| Bem imóvel | `bem_imovel` | `bens[]` |
| Bem veículo | `bem_veiculo` | `bens[]` |
