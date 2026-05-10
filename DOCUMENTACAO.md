# Documentação do Projeto — Skill IRPF OCR DEC

## 1. Objetivo do projeto

Este projeto tem como objetivo construir uma skill/agente para auxiliar na geração da Declaração de Imposto de Renda Pessoa Física brasileira a partir de documentos digitalizados.

A skill deverá ser capaz de:

* receber documentos como PDFs, imagens e comprovantes;
* classificar o tipo de documento;
* extrair dados relevantes por OCR ou leitura assistida;
* normalizar os dados extraídos;
* validar CPF, CNPJ, valores, datas e campos obrigatórios;
* gerar um JSON canônico revisável;
* gerar um relatório humano em Markdown;
* futuramente gerar um arquivo `.DEC` importável no PGD oficial da Receita Federal.

A skill não deve substituir o PGD, contador ou revisão humana. Ela será um pré-processador inteligente para reduzir digitação manual e organizar os dados.

---

## 2. Filosofia do projeto

A ideia central é não transformar diretamente documentos em `.DEC`.

O fluxo correto é:

```text
Documentos reais
    ↓
OCR / extração
    ↓
Dados extraídos estruturados
    ↓
Normalização
    ↓
Validação
    ↓
JSON canônico revisável
    ↓
Relatório humano
    ↓
Revisão do usuário
    ↓
Geração experimental do .DEC
```

A separação mais importante do projeto é:

### Parte probabilística

Inclui tudo que pode ter incerteza:

* OCR;
* leitura de documentos;
* classificação automática;
* extração de campos;
* interpretação de layout.

### Parte determinística

Inclui tudo que precisa ser previsível:

* normalização;
* validação;
* cálculo;
* geração do JSON canônico;
* geração do relatório;
* futuramente serialização do `.DEC`.

O OCR pode errar. Por isso, os dados passam por validação e revisão humana antes de qualquer geração de `.DEC`.

---

## 3. Escopo inicial

A primeira versão do projeto não tentará cobrir todos os casos de IRPF.

O escopo inicial é:

* declarante simples;
* informe de rendimentos PJ;
* recibos médicos, futuramente;
* plano de saúde, futuramente;
* bens simples, futuramente;
* geração de JSON canônico;
* validação local;
* relatório humano.

Nesta fase, o projeto ainda não gera `.DEC`.

A primeira entrega prática é:

> Ler dados estruturados ou extraídos, normalizar, validar e gerar um JSON canônico revisável com relatório humano.

---

## 4. Estrutura atual do projeto

A estrutura atual planejada/implementada é:

```text
irpf_ocr_dec/
├── README.md
├── skill/
│   ├── SKILL.md
│   ├── instructions.md
│   └── schemas/
│       └── canonical_irpf_2026.json
├── tools/
│   ├── normalize.py
│   ├── validate.py
│   ├── check_json.py
│   ├── report.py
│   ├── pipeline.py
│   └── build_canonical_json.py
└── tests/
    └── fixtures/
        ├── assalariado_simples.json
        └── extracted/
            └── informe_pj_exemplo.json
```

Além disso, durante os testes, alguns arquivos de saída podem ser gerados na raiz do projeto:

```text
irpf-gerado.json
irpf-gerado.report.md
assalariado_simples.report.md
irpf-2026.report.md
```

---

## 5. Componentes atuais

### 5.1 `tools/normalize.py`

Arquivo responsável por normalizar dados brutos.

Funções já implementadas:

```python
only_digits()
remove_accents()
normalize_name()
money_to_cents()
normalize_date()
```

Exemplos de transformação:

```text
"123.456.789-09"  → "12345678909"
"José da Silva"   → "JOSE DA SILVA"
"R$ 85.000,00"    → 8500000
"01/01/1980"      → "01011980"
```

Essa camada será usada tanto nos dados vindos do OCR quanto nos dados editados manualmente.

---

### 5.2 `tools/validate.py`

Arquivo responsável por validar o JSON canônico e os dados principais.

Funções já implementadas:

```python
validate_cpf()
validate_cnpj()
validate_required_fields()
validate_canonical_irpf()
```

Validações atuais:

* CPF do declarante;
* CNPJ da fonte pagadora;
* campos obrigatórios do declarante;
* valores negativos;
* IRRF maior que rendimento total.

A saída da validação segue a ideia:

```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

Ou, em caso de erro:

```json
{
  "valid": false,
  "errors": [
    {
      "field": "declarante.cpf",
      "message": "CPF inválido."
    }
  ],
  "warnings": []
}
```

---

### 5.3 `tools/check_json.py`

Ferramenta simples para validar um arquivo JSON canônico pelo terminal.

Uso:

```bash
python3 tools/check_json.py tests/fixtures/assalariado_simples.json
```

Ou:

```bash
python3 tools/check_json.py irpf-gerado.json
```

Ela carrega o arquivo, chama `validate_canonical_irpf()` e imprime o resultado no terminal.

---

### 5.4 `tools/report.py`

Arquivo responsável por gerar um relatório humano em Markdown.

Ele recebe um JSON canônico e gera um arquivo `.report.md` contendo:

* aviso de revisão humana;
* dados do declarante;
* status da validação;
* erros encontrados;
* avisos encontrados;
* rendimentos tributáveis PJ;
* pendências de revisão;
* próximos passos.

Exemplo de uso:

```bash
python3 tools/report.py tests/fixtures/assalariado_simples.json irpf-2026.report.md
```

---

### 5.5 `tools/pipeline.py`

Pipeline inicial do projeto.

Atualmente ele faz:

```text
JSON canônico
    ↓
Validação
    ↓
Relatório Markdown
```

Uso:

```bash
python3 tools/pipeline.py tests/fixtures/assalariado_simples.json
```

Ou:

```bash
python3 tools/pipeline.py irpf-gerado.json
```

Ele gera automaticamente um relatório com base no nome do arquivo de entrada.

---

### 5.6 `tools/build_canonical_json.py`

Arquivo responsável por transformar uma extração simulada em JSON canônico.

Entrada atual:

```text
tests/fixtures/extracted/informe_pj_exemplo.json
```

Saída atual:

```text
irpf-gerado.json
```

Uso:

```bash
python3 tools/build_canonical_json.py tests/fixtures/extracted/informe_pj_exemplo.json irpf-gerado.json
```

Esse arquivo simula o que futuramente será feito com dados vindos de OCR.

O fluxo atual é:

```text
extração simulada
    ↓
build_canonical_json.py
    ↓
irpf-gerado.json
    ↓
pipeline.py
    ↓
irpf-gerado.report.md
```

---

## 6. JSON canônico

O JSON canônico é o formato interno da declaração.

Ele serve como contrato entre:

* OCR;
* normalização;
* validação;
* relatório;
* futuramente builder `.DEC`.

Exemplo mínimo atual:

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
    "tributaveis_pj": [
      {
        "cnpj_pagador": "11222333000181",
        "nome_pagador": "EMPRESA EXEMPLO LTDA",
        "rendimento_total": 8500000,
        "previdencia_oficial": 850000,
        "decimo_terceiro": 700000,
        "irrf": 425000,
        "irrf_13": 35000,
        "beneficiario": "TITULAR"
      }
    ]
  },
  "pagamentos": [],
  "bens": [],
  "dividas": [],
  "avisos": [],
  "requires_review": []
}
```

Decisões importantes:

* CPF e CNPJ ficam apenas com dígitos;
* datas usam formato `DDMMAAAA`;
* valores monetários ficam em centavos inteiros;
* nomes são normalizados em maiúsculas e sem acentos nesta fase;
* campos incertos devem entrar em `requires_review`.

---

## 7. Extração simulada

Antes de integrar OCR real, usamos uma estrutura simulada de extração.

Exemplo:

```json
{
  "document_type": "informe_rendimentos_pj",
  "source_file": "informe_empresa_exemplo.pdf",
  "fields": {
    "cpf_declarante": {
      "value": "123.456.789-09",
      "confidence": "high",
      "source_hint": "Página 1, identificação do beneficiário"
    },
    "rendimento_total": {
      "value": "R$ 85.000,00",
      "confidence": "high",
      "source_hint": "Página 1, quadro 3, linha 1"
    }
  }
}
```

Cada campo extraído deve conter:

* `value`: valor bruto extraído;
* `confidence`: nível de confiança;
* `source_hint`: indicação de onde o dado veio.

Valores possíveis de confiança:

```text
high
medium
low
missing
```

Campos com confiança `low` ou ausentes entram em `requires_review`.

---

## 8. Estado atual do projeto

Até agora já foi feito:

* criação da estrutura básica de pastas;
* implementação de normalizadores;
* implementação de validadores de CPF e CNPJ;
* criação de fixture de JSON canônico;
* criação de ferramenta para validar JSON;
* criação de relatório humano em Markdown;
* criação de pipeline simples;
* criação de extração simulada de informe PJ;
* criação de builder para converter extração simulada em JSON canônico.

Ainda não foi feito:

* OCR real;
* classificação automática de documentos;
* suporte a recibo médico;
* suporte a plano de saúde;
* suporte a bens;
* schema JSON formal completo;
* builder `.DEC`;
* parser reverso `.DEC`;
* integração real com Agno.

---

## 9. Comandos úteis atuais

Entrar na pasta do projeto:

```bash
cd ~/Documents/irpf_ocr_dec
```

Rodar normalizadores manualmente:

```bash
python3 tools/normalize.py
```

Rodar validadores manualmente:

```bash
python3 tools/validate.py
```

Validar fixture canônico:

```bash
python3 tools/check_json.py tests/fixtures/assalariado_simples.json
```

Gerar relatório de um JSON canônico:

```bash
python3 tools/report.py tests/fixtures/assalariado_simples.json irpf-2026.report.md
```

Rodar pipeline com JSON canônico:

```bash
python3 tools/pipeline.py tests/fixtures/assalariado_simples.json
```

Gerar JSON canônico a partir da extração simulada:

```bash
python3 tools/build_canonical_json.py tests/fixtures/extracted/informe_pj_exemplo.json irpf-gerado.json
```

Rodar pipeline no JSON gerado:

```bash
python3 tools/pipeline.py irpf-gerado.json
```

Abrir pasta do projeto no Finder:

```bash
open .
```

Abrir relatório gerado:

```bash
open irpf-gerado.report.md
```

---

## 10. Próximas etapas

### Próxima etapa imediata

Criar um pipeline mais completo que aceite a extração simulada diretamente.

Fluxo desejado:

```text
arquivo extraído
    ↓
gerar JSON canônico
    ↓
validar JSON
    ↓
gerar relatório
```

Em vez de rodar dois comandos:

```bash
python3 tools/build_canonical_json.py tests/fixtures/extracted/informe_pj_exemplo.json irpf-gerado.json
python3 tools/pipeline.py irpf-gerado.json
```

Queremos futuramente rodar algo como:

```bash
python3 tools/pipeline.py --from-extracted tests/fixtures/extracted/informe_pj_exemplo.json
```

ou criar outro comando específico.

---

### Etapas futuras

1. Melhorar o pipeline.
2. Criar schema JSON formal.
3. Adicionar suporte a recibo médico.
4. Adicionar suporte a plano de saúde.
5. Criar classificador simples de documentos.
6. Simular OCR real com arquivos `.txt` ou `.json`.
7. Integrar OCR real.
8. Criar builder `.DEC` experimental.
9. Criar parser reverso `.DEC`.
10. Integrar tudo como skill/agente no Agno.

---

## 11. Decisões técnicas registradas

### 11.1 Não começar pelo `.DEC`

A geração do `.DEC` será feita apenas depois que o JSON canônico estiver estável.

Motivo:

* o `.DEC` é sensível a leiaute, encoding, ordem de campos e hashes;
* OCR é probabilístico;
* o usuário precisa revisar os dados antes;
* o builder `.DEC` deve ser determinístico.

### 11.2 Valores monetários em centavos

Todos os valores monetários do JSON canônico devem ser inteiros em centavos.

Exemplo:

```text
R$ 85.000,00 → 8500000
```

Isso evita problemas de arredondamento com `float`.

### 11.3 Revisão humana obrigatória

Campos incertos, ausentes ou com baixa confiança não devem ser aceitos silenciosamente.

Eles devem aparecer em:

```json
"requires_review": []
```

E depois no relatório humano.

### 11.4 Separar skill de tools

A skill conterá conhecimento, instruções e schemas.

As tools Python executarão lógica determinística.

Separação esperada:

```text
skill/ → conhecimento e comportamento do agente
tools/ → execução confiável e testável
```

---

## 12. Observações importantes

Este projeto lida com dados fiscais sensíveis.

Por isso:

* não devemos usar dados reais sem anonimização nos testes;
* documentos reais devem ser tratados com cuidado;
* logs não devem expor CPF, CNPJ ou valores sem necessidade;
* o usuário sempre deve conferir tudo no PGD oficial;
* a skill não deve prometer transmissão nem substituição de contador.

---

## 13. Histórico do desenvolvimento

### Estado inicial

Foi definido que o projeto será desenvolvido passo a passo para fins de aprendizado.

### Primeiros passos concluídos

* criação da pasta `irpf_ocr_dec` em `~/Documents`;
* criação das pastas `skill`, `tools` e `tests`;
* implementação de `normalize.py`;
* correção do erro de execução causado por rodar o comando fora da pasta do projeto;
* implementação de `validate.py`;
* implementação de `check_json.py`;
* implementação de `report.py`;
* geração do primeiro relatório Markdown;
* implementação de `pipeline.py`;
* implementação de `build_canonical_json.py`;
* criação da extração simulada de um informe de rendimentos PJ.

### Próximo registro esperado

Adicionar um pipeline que execute de ponta a ponta:

```text
extração simulada → JSON canônico → validação → relatório
```
