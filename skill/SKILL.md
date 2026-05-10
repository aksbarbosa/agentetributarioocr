# Skill — IRPF OCR DEC

## Objetivo

Esta skill auxilia na montagem inicial da Declaração de Imposto de Renda Pessoa Física brasileira a partir de documentos fiscais digitalizados, textos extraídos ou extrações estruturadas.

O objetivo é transformar documentos fiscais em um JSON canônico revisável, validado e acompanhado de relatório humano.

No futuro, a skill poderá gerar um arquivo `.DEC` experimental importável no PGD oficial da Receita Federal.

---

## Aviso importante

Esta skill não substitui:

- o PGD oficial da Receita Federal;
- um contador;
- a revisão humana;
- a responsabilidade do contribuinte.

A skill não transmite declaração, não gera recibo `.REC` e não deve prometer conformidade fiscal automática.

---

## Estado atual

Atualmente o projeto possui:

- extrações simuladas em JSON;
- classificador simples por texto bruto;
- simulador local de agente individual;
- simulador local de agente em lote;
- pipeline determinístico;
- relatório humano;
- testes automatizados.

Ainda não possui:

- OCR real;
- leitura direta de PDF/imagem;
- geração `.DEC`;
- agente Agno final.

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
validação da configuração
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

## Classificador simples

Arquivo:

```text
tools/classify_document.py
```

Tipos reconhecidos:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
desconhecido
```

Comandos:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

---

## Simulador local de agente

Arquivo:

```text
tools/agent_simulator.py
```

Comandos:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

A decisão contém:

```text
input_path
classification
decision
```

---

## Simulador local de agente em lote

Arquivo:

```text
tools/agent_batch_simulator.py
```

Comandos:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md
```

Gera:

```text
outputs/agent-decisions.json
outputs/agent-decisions.report.md
```

Esse fluxo permite testar uma primeira versão de orquestração sobre múltiplos documentos, ainda sem OCR real e sem integração Agno.

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
- identificação de baixa confiança.

### Camada determinística atual

- classificação simples por palavras-chave;
- simulação local de decisão;
- normalização;
- validação;
- geração de JSON canônico;
- consolidação;
- relatório.

---

## Configuração

Arquivo:

```text
config/project_config.json
```

Validação:

```bash
python3 tools/validate_config.py config/project_config.json
```

---

## Comando principal

```bash
python3 tools/run_project.py
```

---

## JSON canônico

Formato interno principal:

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

## Validações atuais

A skill já valida:

- configuração;
- CPF;
- CNPJ;
- datas;
- campos obrigatórios;
- pagamentos;
- bens imóveis;
- bens veículos;
- duplicidades simples;
- conflitos de declarante.

---

## Testes

```bash
python3 tests/run_tests.py
python3 tools/dev_check.py
```

---

## Limitações atuais

A skill ainda não faz:

- OCR real;
- leitura direta de PDF/imagem;
- classificação robusta de documentos reais;
- geração `.DEC`;
- transmissão da declaração;
- parser reverso `.DEC`;
- cálculo completo de imposto.

---

## Próximos passos

1. Melhorar o simulador local em lote.
2. Melhorar o simulador local individual.
3. Melhorar o classificador simples.
4. Preparar OCR real.
5. Criar camada de leitura PDF/imagem.
6. Integrar ao Agno.
