# Pipeline — IRPF OCR DEC

Este arquivo documenta o fluxo atual do projeto.

O pipeline atual trabalha com:

- extrações simuladas em JSON;
- textos brutos simulados para classificação;
- classificador simples por palavras-chave;
- simulador local de agente;
- validação e consolidação determinística.

Ainda não há OCR real, leitura direta de PDF/imagem ou geração `.DEC`.

---

## Objetivo

Transformar arquivos estruturados em:

```text
inputs/extracted/
```

em:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
```

Além disso, o projeto possui uma etapa inicial de classificação simples de textos brutos simulados:

```text
tests/fixtures/raw_text/
    ↓
tools/classify_document.py
    ↓
document_type provável
```

E uma etapa inicial de simulação local de agente:

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

---

## Fluxo geral atual

### 1. Classificação simples

```text
texto bruto simulado
    ↓
tools/classify_document.py
    ↓
document_type provável
```

### 2. Simulação local de agente

```text
texto bruto simulado
    ↓
tools/agent_simulator.py
    ↓
classificação
    ↓
decisão estruturada
    ↓
schema recomendado
    ↓
próximo passo sugerido
```

### 3. Pipeline principal

```text
config/project_config.json
    ↓
tools/run_project.py
    ↓
validação da configuração
    ↓
inputs/extracted/*.json
    ↓
validação das extrações
    ↓
conversão para JSON canônico parcial
    ↓
consolidação
    ↓
detecção simples de duplicidades
    ↓
validação canônica
    ↓
geração do relatório humano
    ↓
outputs/
```

---

## Classificador simples

O classificador simples está em:

```text
tools/classify_document.py
```

Ele recebe um arquivo de texto e tenta identificar o `document_type`.

Exemplo:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Saída esperada:

```text
Classificação do documento:
- document_type: bem_veiculo
- label: Bem veículo
- confidence: high
```

Também pode imprimir saída JSON:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Tipos reconhecidos atualmente:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
desconhecido
```

O classificador atual é determinístico e baseado em palavras-chave. Ele ainda não substitui OCR real nem classificação robusta por IA.

---

## Simulador local de agente

O simulador local está em:

```text
tools/agent_simulator.py
```

Ele recebe texto bruto, chama o classificador simples e retorna uma decisão estruturada.

Exemplo:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Saída esperada:

```text
Simulação do agente

Classificação:
- document_type: bem_veiculo
- label: Bem veículo
- confidence: high

Decisão:
- Deve continuar: True
- Schema recomendado: skill/schemas/extracted_bem_veiculo.json
```

Também pode imprimir a decisão em JSON no terminal:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Também pode salvar a decisão estruturada em arquivo:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

Para conferir:

```bash
cat outputs/agent-decision.json
```

O arquivo salvo contém:

```text
input_path
classification
decision
```

A seção `classification` contém, entre outros campos:

```text
document_type
label
confidence
scores
matched_keywords
best_score
second_score
```

A seção `decision` contém:

```text
document_type
confidence
should_continue
schema_path
next_step
```

O campo `should_continue` indica se a classificação tem confiança suficiente para seguir.

O campo `schema_path` indica qual schema de extração estruturada deve ser usado como referência.

O campo `next_step` descreve a próxima ação recomendada.

Esse simulador ainda não é o agente Agno final. Ele serve para testar localmente a lógica de decisão antes da integração com Agno.

---

## Fixtures de texto bruto

As fixtures atuais ficam em:

```text
tests/fixtures/raw_text/
```

Arquivos atuais:

```text
crlv_veiculo_exemplo.txt
informe_pj_exemplo.txt
iptu_imovel_exemplo.txt
plano_saude_exemplo.txt
recibo_medico_exemplo.txt
```

Esses arquivos simulam textos que futuramente poderiam vir de OCR.

---

## Comando principal

```bash
python3 tools/run_project.py
```

Esse comando:

1. carrega `config/project_config.json`;
2. valida a configuração com `tools/validate_config.py`;
3. lê os arquivos de `inputs/extracted/`;
4. valida cada extração com `tools/validate_extracted.py`;
5. converte cada extração com `tools/build_canonical_json.py`;
6. consolida os dados com `tools/pipeline_batch.py`;
7. valida o JSON consolidado com `tools/validate.py`;
8. gera relatório com `tools/report.py`.

---

## Configuração

O pipeline usa:

```text
config/project_config.json
```

Exemplo:

```json
{
  "project_name": "IRPF OCR DEC",
  "schema_version": "irpf-2026-v1",
  "exercicio": 2026,
  "ano_calendario": 2025,
  "tipo_declaracao": "AJUSTE_ANUAL",
  "modelo": "AUTO",
  "input_raw_dir": "inputs/raw",
  "input_extracted_dir": "inputs/extracted",
  "output_dir": "outputs",
  "output_json": "outputs/irpf-consolidado.json",
  "output_report": "outputs/irpf-consolidado.report.md",
  "fail_on_invalid_extraction": false,
  "fail_on_canonical_error": true,
  "enable_duplicate_detection": true,
  "enable_human_review_report": true
}
```

O schema formal da configuração está em:

```text
skill/schemas/project_config.json
```

A validação prática é feita por:

```text
tools/validate_config.py
```

---

## Tipos de documentos suportados

Atualmente o pipeline suporta:

| `document_type` | Destino |
|---|---|
| `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| `recibo_medico` | `pagamentos[]` |
| `plano_saude` | `pagamentos[]` |
| `bem_imovel` | `bens[]` |
| `bem_veiculo` | `bens[]` |

---

## Entradas atuais

A pasta atual de entrada do pipeline canônico é:

```text
inputs/extracted/
```

Arquivos de exemplo atuais:

```text
informe_pj_exemplo.json
recibo_medico_exemplo.json
plano_saude_exemplo.json
bem_imovel_exemplo.json
bem_veiculo_exemplo.json
```

---

## Saídas atuais

O pipeline gera:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
```

O simulador local pode gerar:

```text
outputs/agent-decision.json
```

O JSON consolidado contém:

```text
declarante
rendimentos.tributaveis_pj[]
pagamentos[]
bens[]
dividas[]
avisos[]
requires_review[]
```

O relatório humano contém:

```text
Declarante
Validação
Avisos do processamento
Rendimentos tributáveis PJ
Pagamentos
Bens e direitos
Detalhes de imóvel
Detalhes de veículo
Pendências de revisão
Próximos passos
```

---

## Tratamento de extrações inválidas

A flag:

```json
"fail_on_invalid_extraction": false
```

faz com que extrações inválidas sejam ignoradas e registradas em:

```text
Arquivos ignorados
```

Se for alterada para:

```json
"fail_on_invalid_extraction": true
```

extrações inválidas passam a ser fatais.

---

## Tratamento de erro canônico

A flag:

```json
"fail_on_canonical_error": true
```

faz o pipeline falhar quando o JSON consolidado for inválido.

---

## Detecção de duplicidades

A flag:

```json
"enable_duplicate_detection": true
```

ativa detecção simples de pagamentos duplicados.

A detecção atual não remove dados. Ela apenas adiciona avisos em:

```json
"avisos": []
```

---

## Relatório humano

A flag:

```json
"enable_human_review_report": true
```

ativa a geração do relatório Markdown.

---

## Comandos úteis

Rodar classificador simples:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Rodar classificador simples com saída JSON:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Rodar simulador local de agente:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Rodar simulador local de agente com saída JSON no terminal:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Salvar decisão estruturada do simulador:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

Rodar pipeline principal:

```bash
python3 tools/run_project.py
```

Rodar pipeline em lote diretamente:

```bash
python3 tools/pipeline_batch.py inputs/extracted
```

Rodar pipeline em lote usando config:

```bash
python3 tools/pipeline_batch.py --config config/project_config.json
```

Validar configuração:

```bash
python3 tools/validate_config.py config/project_config.json
```

Rodar checagem completa:

```bash
python3 tools/dev_check.py
```

---

## Testes relacionados

O classificador possui teste automatizado em:

```text
tests/unit/test_classify_document.py
```

O simulador local possui teste automatizado em:

```text
tests/unit/test_agent_simulator.py
```

As fixtures usadas pelos testes ficam em:

```text
tests/fixtures/raw_text/
```

O pipeline principal é coberto por:

```text
tests/unit/test_pipeline_batch.py
tests/unit/test_run_project.py
```

---

## Estado atual

O pipeline local com extrações simuladas está funcional para cinco tipos:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
```

O classificador simples também reconhece esses tipos, além de:

```text
desconhecido
```

O simulador local já consegue:

```text
classificar texto bruto
decidir se deve continuar
indicar schema recomendado
sugerir próximo passo
imprimir JSON
salvar decisão estruturada em arquivo
```

Ainda não há OCR real, leitura direta de PDF/imagem, classificação robusta nem geração `.DEC`.

---

## Próximas etapas

1. Atualizar `CHANGELOG.md` com `--save-json`.
2. Melhorar o simulador local de agente.
3. Melhorar o classificador simples.
4. Preparar OCR real.
5. Criar camada de leitura de PDF/imagem.
6. Integrar a lógica ao agente Agno.
