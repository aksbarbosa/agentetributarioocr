# Skill — IRPF OCR DEC

## Objetivo

Esta skill auxilia na montagem inicial da Declaração de Imposto de Renda Pessoa Física brasileira a partir de documentos fiscais digitalizados, textos extraídos ou extrações estruturadas.

O objetivo é transformar documentos fiscais em JSON canônico revisável, validado e acompanhado de relatório humano.

No futuro, a skill poderá gerar um arquivo `.DEC` experimental importável no PGD oficial da Receita Federal.

---

## Aviso importante

Esta skill não substitui PGD oficial, contador, revisão humana ou responsabilidade do contribuinte.

A skill não transmite declaração, não gera recibo `.REC` e não deve prometer conformidade fiscal automática.

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
outputs/agent-decisions.json
    ↓
outputs/agent-decisions.report.md
```

### Pipeline principal

```text
inputs/extracted/
    ↓
tools/run_project.py
    ↓
JSON canônico consolidado
    ↓
relatório humano
```

---

## Comandos

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
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md --json
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown
```

Pipeline:

```bash
python3 tools/run_project.py
python3 tools/dev_check.py
```

---

## Relatório do simulador em lote

O relatório Markdown gerado por:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown
```

possui uma seção específica de status:

```markdown
## Status dos documentos

### Aptos a continuar

### Exigem revisão
```

e uma seção detalhada:

```markdown
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

---

## Arquitetura

### Camada probabilística futura

- OCR;
- leitura de documentos;
- classificação semântica;
- extração de campos;
- baixa confiança.

### Camada determinística atual

- classificação simples por palavras-chave;
- simulação local de decisão;
- normalização;
- validação;
- geração de JSON canônico;
- consolidação;
- relatório.

---

## JSON canônico

```json
{
  "$schema": "irpf-2026-v1",
  "exercicio": 2026,
  "ano_calendario": 2025,
  "tipo_declaracao": "AJUSTE_ANUAL",
  "modelo": "AUTO",
  "declarante": {},
  "rendimentos": {
    "tributaveis_pj": []
  },
  "pagamentos": [],
  "bens": [],
  "dividas": [],
  "avisos": [],
  "requires_review": []
}
```

---

## Próximos passos

1. Melhorar o simulador local em lote.
2. Melhorar o simulador local individual.
3. Melhorar o classificador simples.
4. Preparar OCR real.
5. Criar leitura PDF/imagem.
6. Integrar ao Agno.
