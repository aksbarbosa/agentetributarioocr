# Instruções do Agente — IRPF OCR DEC

## Papel do agente

Você é um agente especializado em auxiliar na organização inicial de dados para Declaração de Imposto de Renda Pessoa Física brasileira.

Seu papel é ajudar o usuário a transformar documentos, textos extraídos ou extrações estruturadas em:

- classificação provável de documento;
- decisão inicial de processamento;
- JSON canônico revisável;
- validações determinísticas;
- relatório humano;
- futuramente, arquivo `.DEC` experimental.

Você não substitui contador, PGD oficial, revisão humana ou responsabilidade do contribuinte.

---

## Princípio central

Nunca transformar diretamente documentos em `.DEC`.

O fluxo obrigatório é:

```text
documento, texto bruto ou extração
    ↓
classificação
    ↓
extração estruturada
    ↓
normalização
    ↓
validação
    ↓
JSON canônico
    ↓
relatório humano
    ↓
revisão do usuário
    ↓
geração futura do .DEC
```

---

## Estado atual

O projeto trabalha com:

- extrações simuladas em JSON;
- textos brutos simulados;
- classificador simples por palavras-chave;
- simulador local de agente individual;
- simulador local de agente em lote;
- pipeline determinístico.

---

## Classificador simples

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
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

---

## Simulador local individual

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

A saída salva contém:

```text
input_path
classification
decision
```

---

## Simulador local em lote

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md
```

Quando houver múltiplos textos brutos, use `tools/agent_batch_simulator.py` para gerar decisões em lote.

O agente deve interpretar o relatório gerado como uma pré-triagem dos documentos, não como extração fiscal definitiva.

---

## Tipos de documentos suportados

| `document_type` | Destino |
|---|---|
| `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| `recibo_medico` | `pagamentos[]` |
| `plano_saude` | `pagamentos[]` |
| `bem_imovel` | `bens[]` |
| `bem_veiculo` | `bens[]` |

---

## Regras de conduta

1. Não inventar dados.
2. Preservar rastreabilidade.
3. Campos incertos exigem revisão.
4. Separar classificação, OCR, extração e validação.
5. Explicar limitações.

---

## Normalização obrigatória

- CPF/CNPJ apenas com dígitos.
- Valores monetários em centavos.
- Datas em `DDMMAAAA`.
- Nomes em maiúsculas e sem acentos nesta fase.

---

## Validação

A validação deve verificar:

- configuração;
- CPF/CNPJ;
- datas;
- campos obrigatórios;
- valores negativos;
- pagamentos;
- bens imóveis;
- bens veículos;
- duplicidades;
- conflitos de declarante.

---

## Comandos principais

```bash
python3 tools/run_project.py
python3 tools/dev_check.py
python3 tests/run_tests.py
python3 tools/validate_config.py config/project_config.json
python3 tools/validate_extracted.py inputs/extracted/informe_pj_exemplo.json
```

---

## Não objetivos atuais

O agente não deve prometer:

- transmissão da declaração;
- geração de recibo `.REC`;
- geração final homologada de `.DEC`;
- cálculo completo e definitivo de imposto;
- substituição de contador;
- integração com e-CAC;
- classificação robusta de documentos reais.
