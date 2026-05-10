# Skill — IRPF OCR DEC

## Objetivo

Esta skill auxilia na montagem inicial da Declaração de Imposto de Renda Pessoa Física brasileira a partir de documentos fiscais digitalizados ou extrações estruturadas.

O objetivo é transformar documentos como informes de rendimentos, recibos médicos, informes de plano de saúde e documentos de bens em um JSON canônico revisável, validado e acompanhado de relatório humano.

No futuro, a skill poderá gerar um arquivo `.DEC` experimental importável no PGD oficial da Receita Federal.

---

## Aviso importante

Esta skill não substitui:

- o PGD oficial da Receita Federal;
- um contador;
- a revisão humana;
- a responsabilidade do contribuinte.

A skill não transmite declaração, não gera recibo `.REC` e não deve prometer conformidade fiscal automática.

O fluxo correto é sempre:

```text
documento
    ↓
classificação
    ↓
extração
    ↓
JSON canônico
    ↓
validação
    ↓
relatório humano
    ↓
revisão do usuário
    ↓
geração futura do .DEC
```

Nunca pular diretamente de documento para `.DEC`.

---

## Estado atual

A skill ainda está em fase inicial.

Atualmente o projeto:

- processa extrações simuladas em JSON;
- possui classificador simples por texto bruto simulado;
- ainda não possui OCR real;
- ainda não lê PDF ou imagem diretamente;
- ainda não gera `.DEC`.

Fluxo atual do classificador:

```text
tests/fixtures/raw_text/
    ↓
tools/classify_document.py
    ↓
document_type provável
```

Fluxo atual do pipeline principal:

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

O projeto possui um classificador inicial baseado em palavras-chave:

```text
tools/classify_document.py
```

Ele recebe texto bruto e tenta identificar o `document_type`.

Tipos reconhecidos atualmente:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
desconhecido
```

Exemplo de uso:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Exemplo de saída:

```text
Classificação do documento:
- document_type: bem_veiculo
- label: Bem veículo
- confidence: high
```

Fixtures atuais de texto bruto:

```text
tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
tests/fixtures/raw_text/informe_pj_exemplo.txt
tests/fixtures/raw_text/iptu_imovel_exemplo.txt
tests/fixtures/raw_text/plano_saude_exemplo.txt
tests/fixtures/raw_text/recibo_medico_exemplo.txt
```

O classificador ainda não substitui OCR nem classificação robusta por IA. Ele é uma primeira camada determinística para textos já extraídos.

---

## Documentos suportados atualmente

### 1. Informe de rendimentos PJ

Tipo de extração:

```json
{
  "document_type": "informe_rendimentos_pj"
}
```

Gera dados em:

```json
{
  "rendimentos": {
    "tributaveis_pj": []
  }
}
```

---

### 2. Recibo médico

Tipo de extração:

```json
{
  "document_type": "recibo_medico"
}
```

Gera dados em:

```json
{
  "pagamentos": []
}
```

com código de pagamento:

```json
{
  "codigo": "10"
}
```

---

### 3. Plano de saúde

Tipo de extração:

```json
{
  "document_type": "plano_saude"
}
```

Gera dados em:

```json
{
  "pagamentos": []
}
```

com código de pagamento:

```json
{
  "codigo": "26"
}
```

---

### 4. Bem imóvel

Tipo de extração:

```json
{
  "document_type": "bem_imovel"
}
```

Gera dados em:

```json
{
  "bens": []
}
```

Nesta fase, o caso implementado é um imóvel simples, como apartamento residencial.

Código usado no exemplo atual:

```text
tipo_bem = IMOVEL
grupo_bem = 01
codigo_bem = 11
```

---

### 5. Bem veículo

Tipo de extração:

```json
{
  "document_type": "bem_veiculo"
}
```

Gera dados em:

```json
{
  "bens": []
}
```

Nesta fase, o caso implementado é um veículo automotor terrestre.

Código usado no exemplo atual:

```text
tipo_bem = VEICULO
grupo_bem = 02
codigo_bem = 01
```

---

## Arquitetura

A skill separa duas camadas.

### Camada probabilística

Responsável por tarefas com incerteza:

- OCR;
- leitura de documentos;
- classificação semântica de documentos;
- extração de campos;
- identificação de baixa confiança.

Essa camada ainda será implementada futuramente.

### Camada determinística

Responsável por lógica previsível e testável:

- classificação simples por palavras-chave;
- normalização;
- validação;
- geração de JSON canônico;
- consolidação;
- detecção de duplicidades;
- geração de relatório.

Essa camada já está parcialmente implementada em `tools/`.

---

## Estrutura relevante

```text
irpf_ocr_dec/
├── config/
│   └── project_config.json
├── inputs/
│   ├── raw/
│   └── extracted/
├── outputs/
│   ├── irpf-consolidado.json
│   └── irpf-consolidado.report.md
├── skill/
│   ├── SKILL.md
│   ├── instructions.md
│   ├── references/
│   │   ├── codigos_bens.md
│   │   ├── codigos_pagamentos.md
│   │   ├── json_canonico.md
│   │   ├── pipeline.md
│   │   └── tipos_documentos.md
│   └── schemas/
│       ├── canonical_irpf_2026.json
│       ├── extracted_bem_imovel.json
│       ├── extracted_bem_veiculo.json
│       ├── extracted_informe_pj.json
│       ├── extracted_plano_saude.json
│       ├── extracted_recibo_medico.json
│       └── project_config.json
├── tests/
│   ├── fixtures/
│   │   └── raw_text/
│   ├── run_tests.py
│   └── unit/
└── tools/
    ├── normalize.py
    ├── classify_document.py
    ├── validate.py
    ├── validate_config.py
    ├── validate_extracted.py
    ├── build_canonical_json.py
    ├── report.py
    ├── pipeline_batch.py
    ├── clean_outputs.py
    ├── dev_check.py
    └── run_project.py
```

---

## Configuração

A skill usa o arquivo:

```text
config/project_config.json
```

Esse arquivo define:

- nome do projeto;
- exercício;
- ano-calendário;
- versão do schema;
- tipo de declaração;
- modelo;
- pastas de entrada;
- caminhos de saída;
- flags de comportamento do pipeline.

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

A validação prática da configuração é feita por:

```text
tools/validate_config.py
```

O comando principal valida essa configuração automaticamente antes de rodar o pipeline.

O schema formal da configuração está em:

```text
skill/schemas/project_config.json
```

---

## Comando principal

Para rodar o projeto atual:

```bash
python3 tools/run_project.py
```

Esse comando:

1. lê `config/project_config.json`;
2. valida a configuração;
3. processa os arquivos em `inputs/extracted/`;
4. gera `outputs/irpf-consolidado.json`;
5. gera `outputs/irpf-consolidado.report.md`.

---

## Contrato de entrada atual

A entrada atual da skill é uma extração estruturada em JSON.

Todo arquivo de extração deve ter:

```json
{
  "document_type": "...",
  "source_file": "...",
  "fields": {}
}
```

Cada campo extraído deve ter:

```json
{
  "value": "...",
  "confidence": "high | medium | low",
  "source_hint": "..."
}
```

Campos com `confidence = "low"` devem gerar pendência de revisão humana.

---

## JSON canônico

O JSON canônico é o formato interno da declaração.

Exemplo simplificado:

```json
{
  "$schema": "irpf-2026-v1",
  "exercicio": 2026,
  "ano_calendario": 2025,
  "tipo_declaracao": "AJUSTE_ANUAL",
  "modelo": "AUTO",
  "declarante": {
    "cpf": "12345678909",
    "nome": "JOSE DA SILVA",
    "data_nascimento": "01011980"
  },
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

## Conversões atuais

| Documento | `document_type` | Destino |
|---|---|---|
| Informe de rendimentos PJ | `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| Recibo médico | `recibo_medico` | `pagamentos[]` |
| Plano de saúde | `plano_saude` | `pagamentos[]` |
| Bem imóvel | `bem_imovel` | `bens[]` |
| Bem veículo | `bem_veiculo` | `bens[]` |

---

## Regras de normalização

- CPF e CNPJ devem conter apenas dígitos.
- Datas devem usar formato `DDMMAAAA`.
- Valores monetários devem ser inteiros em centavos.
- Nomes devem ser normalizados em maiúsculas.
- Campos incertos devem ser enviados para revisão.

Exemplos:

```text
123.456.789-09 → 12345678909
R$ 500,00 → 50000
R$ 80.000,00 → 8000000
15/03/2025 → 15032025
José da Silva → JOSE DA SILVA
Toyota → TOYOTA
```

---

## Validações atuais

A skill já valida:

- configuração do projeto;
- CPF do declarante;
- data de nascimento;
- CNPJ de fonte pagadora;
- CPF/CNPJ de prestador;
- campos obrigatórios;
- valores monetários negativos;
- pagamento com valor zero;
- códigos de pagamento `10` e `26`;
- bens imóveis básicos;
- bens veículos básicos;
- CEP;
- UF;
- RENAVAM;
- placa;
- marca, modelo e ano de fabricação;
- data de aquisição de bem;
- duplicidade simples de pagamentos;
- conflitos em dados do declarante.

---

## Saídas

A execução principal gera:

### JSON consolidado

```text
outputs/irpf-consolidado.json
```

Contém todos os dados normalizados e consolidados.

### Relatório humano

```text
outputs/irpf-consolidado.report.md
```

Contém:

- dados do declarante;
- status de validação;
- avisos de processamento;
- rendimentos tributáveis PJ;
- pagamentos;
- bens e direitos;
- detalhes de imóvel;
- detalhes de veículo;
- pendências de revisão;
- próximos passos.

---

## Referências internas

A pasta:

```text
skill/references/
```

contém documentação auxiliar para a skill.

Arquivos atuais:

```text
codigos_bens.md
codigos_pagamentos.md
json_canonico.md
pipeline.md
tipos_documentos.md
```

Essas referências documentam:

- tipos de documento suportados;
- códigos de pagamento;
- códigos de bens;
- estrutura do JSON canônico;
- funcionamento do pipeline.

---

## Schemas formais

A pasta:

```text
skill/schemas/
```

contém contratos formais em JSON Schema.

Arquivos atuais:

```text
canonical_irpf_2026.json
extracted_bem_imovel.json
extracted_bem_veiculo.json
extracted_informe_pj.json
extracted_plano_saude.json
extracted_recibo_medico.json
project_config.json
```

Esses schemas documentam:

- JSON canônico;
- extrações estruturadas;
- configuração do projeto.

---

## Testes e checagem de desenvolvimento

O projeto possui testes automatizados simples em Python puro.

Para rodar todos os testes:

```bash
python3 tests/run_tests.py
```

Para rodar a checagem completa:

```bash
python3 tools/dev_check.py
```

A checagem completa executa:

1. validação da configuração;
2. limpeza dos outputs;
3. execução do projeto;
4. execução dos testes.

---

## Limitações atuais

A skill ainda não faz:

- OCR real;
- leitura direta de PDF ou imagem;
- classificação automática robusta de documentos reais;
- geração de `.DEC`;
- transmissão da declaração;
- integração com PGD;
- parser reverso `.DEC`;
- cálculo completo de imposto;
- suporte a dependentes;
- suporte a investimentos;
- suporte a GCAP;
- suporte a atividade rural.

---

## Próximos passos

1. Atualizar `skill/instructions.md` com o classificador.
2. Atualizar `skill/references/pipeline.md` com o classificador.
3. Atualizar `CHANGELOG.md` com o classificador.
4. Melhorar o classificador simples.
5. Preparar OCR real.
6. Criar builder `.DEC` experimental.
7. Criar parser reverso `.DEC`.
8. Criar testes adicionais para novos documentos.
9. Integrar a skill ao agente Agno.
