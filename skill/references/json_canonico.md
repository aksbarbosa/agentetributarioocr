# JSON Canônico — IRPF OCR DEC

Este arquivo documenta o formato interno usado pelo projeto para representar uma declaração IRPF antes da geração de relatório ou futura geração de `.DEC`.

O JSON canônico é o contrato central entre:

- extração de documentos;
- normalização;
- validação;
- consolidação;
- relatório humano;
- futura geração `.DEC`.

---

## Objetivo

O JSON canônico serve para transformar diferentes documentos fiscais em uma estrutura única e revisável.

Exemplos de documentos de origem:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
```

Esses documentos são convertidos para seções específicas do JSON canônico:

```text
informe_rendimentos_pj → rendimentos.tributaveis_pj[]
recibo_medico          → pagamentos[]
plano_saude            → pagamentos[]
bem_imovel             → bens[]
bem_veiculo            → bens[]
```

---

## Estrutura raiz

A estrutura atual é:

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

## Campos principais

### `$schema`

Identifica a versão do schema interno.

Valor atual:

```json
"$schema": "irpf-2026-v1"
```

---

### `exercicio`

Ano de exercício da declaração.

Exemplo:

```json
"exercicio": 2026
```

---

### `ano_calendario`

Ano-calendário da declaração.

Exemplo:

```json
"ano_calendario": 2025
```

---

### `tipo_declaracao`

Tipo de declaração.

Valor atual suportado:

```json
"tipo_declaracao": "AJUSTE_ANUAL"
```

---

### `modelo`

Modelo de declaração.

Valores planejados:

```text
AUTO
SIMPLIFICADA
COMPLETA
```

Valor atual usado:

```json
"modelo": "AUTO"
```

---

## `declarante`

Contém os dados básicos do titular da declaração.

Estrutura atual:

```json
{
  "cpf": "12345678909",
  "nome": "JOSE DA SILVA",
  "data_nascimento": "01011980"
}
```

### Campos

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `cpf` | string | 11 dígitos | CPF sem pontos ou hífen |
| `nome` | string | maiúsculo | Nome normalizado |
| `data_nascimento` | string | `DDMMAAAA` | Data de nascimento |

---

## `rendimentos`

Agrupa rendimentos extraídos dos documentos.

Estrutura atual:

```json
{
  "tributaveis_pj": []
}
```

---

## `rendimentos.tributaveis_pj[]`

Usado para informes de rendimentos emitidos por pessoa jurídica.

Origem atual:

```text
document_type = informe_rendimentos_pj
```

Exemplo:

```json
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
```

### Campos

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `cnpj_pagador` | string | 14 dígitos | CNPJ da fonte pagadora |
| `nome_pagador` | string | maiúsculo | Nome da fonte pagadora |
| `rendimento_total` | integer | centavos | Rendimentos tributáveis |
| `previdencia_oficial` | integer | centavos | Previdência oficial |
| `decimo_terceiro` | integer | centavos | 13º salário |
| `irrf` | integer | centavos | Imposto retido |
| `irrf_13` | integer | centavos | IRRF sobre 13º |
| `beneficiario` | string | `TITULAR` ou `DEPENDENTE` | Atualmente usamos `TITULAR` |

---

## `pagamentos[]`

Lista de pagamentos dedutíveis ou informativos.

Origens atuais:

```text
recibo_medico
plano_saude
```

---

## Pagamento médico

Origem:

```text
document_type = recibo_medico
```

Código atual:

```json
"codigo": "10"
```

Exemplo:

```json
{
  "codigo": "10",
  "descricao": "CONSULTA MEDICA",
  "beneficiario_cpf_cnpj": "12345678909",
  "beneficiario_nome": "DRA. MARIA OLIVEIRA",
  "beneficiario_tipo": "T",
  "tipo_documento": 1,
  "valor_pago": 50000,
  "valor_nao_dedutivel": 0,
  "data_pagamento": "15032025"
}
```

### Campos

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `codigo` | string | `"10"` | Código de pagamento médico |
| `descricao` | string | maiúsculo | Descrição do serviço |
| `beneficiario_cpf_cnpj` | string | 11 ou 14 dígitos | CPF/CNPJ do prestador |
| `beneficiario_nome` | string | maiúsculo | Nome do prestador |
| `beneficiario_tipo` | string | `T` ou `D` | Titular ou dependente |
| `tipo_documento` | integer | `1` ou `2` | 1 = CPF, 2 = CNPJ |
| `valor_pago` | integer | centavos | Valor pago |
| `valor_nao_dedutivel` | integer | centavos | Valor não dedutível |
| `data_pagamento` | string | `DDMMAAAA` | Data do pagamento |

---

## Plano de saúde

Origem:

```text
document_type = plano_saude
```

Código atual:

```json
"codigo": "26"
```

Exemplo:

```json
{
  "codigo": "26",
  "descricao": "PLANO DE SAUDE",
  "beneficiario_cpf_cnpj": "11222333000181",
  "beneficiario_nome": "PLANO SAUDE EXEMPLO S.A.",
  "beneficiario_tipo": "T",
  "tipo_documento": 2,
  "valor_pago": 360000,
  "valor_nao_dedutivel": 0
}
```

### Campos

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `codigo` | string | `"26"` | Código de plano de saúde |
| `descricao` | string | maiúsculo | Descrição do pagamento |
| `beneficiario_cpf_cnpj` | string | 14 dígitos | CNPJ da operadora |
| `beneficiario_nome` | string | maiúsculo | Nome da operadora |
| `beneficiario_tipo` | string | `T` ou `D` | Titular ou dependente |
| `tipo_documento` | integer | `2` | CNPJ |
| `valor_pago` | integer | centavos | Valor anual pago |
| `valor_nao_dedutivel` | integer | centavos | Parcela não dedutível |

---

## `bens[]`

Lista de bens e direitos declarados.

Origens atuais:

```text
document_type = bem_imovel
document_type = bem_veiculo
```

Cada bem possui campos comuns e campos específicos por tipo.

---

## Campos comuns de `bens[]`

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `tipo_bem` | string | `IMOVEL` ou `VEICULO` | Tipo interno do bem |
| `grupo_bem` | string | 2 dígitos | Grupo do bem |
| `codigo_bem` | string | 2 dígitos | Código específico do bem |
| `descricao` | string | texto normalizado | Descrição detalhada |
| `valor_anterior` | integer | centavos | Valor em 31/12 do ano anterior |
| `valor_atual` | integer | centavos | Valor em 31/12 do ano-calendário |
| `data_aquisicao` | string | `DDMMAAAA` | Data de aquisição |
| `beneficiario_tipo` | string | `T` ou `D` | Titular ou dependente |

---

## Bem imóvel

Origem:

```text
document_type = bem_imovel
```

Valores atuais:

```text
tipo_bem = IMOVEL
grupo_bem = 01
codigo_bem = 11
```

Exemplo:

```json
{
  "tipo_bem": "IMOVEL",
  "grupo_bem": "01",
  "codigo_bem": "11",
  "descricao": "APARTAMENTO RESIDENCIAL LOCALIZADO NA RUA DAS FLORES, NUMERO 123, BAIRRO CENTRO, SAO PAULO SP",
  "valor_anterior": 25000000,
  "valor_atual": 25000000,
  "endereco": {
    "cep": "01234567",
    "logradouro": "RUA DAS FLORES",
    "numero": "123",
    "bairro": "CENTRO",
    "municipio": "SAO PAULO",
    "uf": "SP"
  },
  "iptu": "1234567890",
  "matricula": "12345",
  "data_aquisicao": "10052020",
  "beneficiario_tipo": "T"
}
```

### Campos específicos de imóvel

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `endereco.cep` | string | 8 dígitos | CEP do imóvel |
| `endereco.logradouro` | string | texto | Logradouro |
| `endereco.numero` | string | texto | Número |
| `endereco.bairro` | string | texto | Bairro |
| `endereco.municipio` | string | texto | Município |
| `endereco.uf` | string | 2 letras | UF |
| `iptu` | string | dígitos | Cadastro municipal/IPTU |
| `matricula` | string | dígitos | Matrícula do imóvel |

---

## Bem veículo

Origem:

```text
document_type = bem_veiculo
```

Valores atuais:

```text
tipo_bem = VEICULO
grupo_bem = 02
codigo_bem = 01
```

Exemplo:

```json
{
  "tipo_bem": "VEICULO",
  "grupo_bem": "02",
  "codigo_bem": "01",
  "descricao": "AUTOMOVEL MARCA TOYOTA, MODELO COROLLA XEI, ANO 2020, PLACA ABC1D23",
  "valor_anterior": 8000000,
  "valor_atual": 8000000,
  "renavam": "12345678901",
  "placa": "ABC1D23",
  "marca": "TOYOTA",
  "modelo": "COROLLA XEI",
  "ano_fabricacao": "2020",
  "data_aquisicao": "20082020",
  "beneficiario_tipo": "T"
}
```

### Campos específicos de veículo

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `renavam` | string | dígitos | Código RENAVAM |
| `placa` | string | texto normalizado | Placa do veículo |
| `marca` | string | texto normalizado | Marca do veículo |
| `modelo` | string | texto normalizado | Modelo do veículo |
| `ano_fabricacao` | string | 4 dígitos | Ano de fabricação |

---

## `dividas[]`

Lista de dívidas e ônus reais.

Ainda não implementado.

---

## `avisos[]`

Lista de avisos gerados durante processamento ou consolidação.

Exemplos:

```text
pagamento possivelmente duplicado
conflito nos dados do declarante
RENAVAM com quantidade incomum de dígitos
placa com tamanho incomum
```

Exemplo:

```json
{
  "field": "pagamentos[1]",
  "message": "Pagamento possivelmente duplicado. Já existe pagamento semelhante em pagamentos[0]."
}
```

Esses avisos não impedem necessariamente o pipeline de concluir, mas devem aparecer no relatório humano.

---

## `requires_review[]`

Lista de pendências de revisão humana.

Usado quando:

- um campo foi extraído com baixa confiança;
- um campo importante precisa ser conferido;
- a extração veio incompleta, mas não bloqueou a conversão.

Exemplo:

```json
{
  "field": "matricula",
  "reason": "Campo extraído com baixa confiança.",
  "source_hint": "Matrícula informada manualmente para fixture",
  "source_file": "inputs/extracted/bem_imovel_exemplo.json"
}
```

---

## Regras de normalização

### CPF/CNPJ

Sempre apenas dígitos.

```text
123.456.789-09 → 12345678909
11.222.333/0001-81 → 11222333000181
```

### Valores monetários

Sempre inteiros em centavos.

```text
R$ 500,00 → 50000
R$ 3.600,00 → 360000
R$ 80.000,00 → 8000000
R$ 85.000,00 → 8500000
R$ 250.000,00 → 25000000
```

### Datas

Formato `DDMMAAAA`.

```text
15/03/2025 → 15032025
10/05/2020 → 10052020
20/08/2020 → 20082020
```

### Nomes

Maiúsculos e sem acentos nesta fase.

```text
José da Silva → JOSE DA SILVA
São Paulo → SAO PAULO
Toyota → TOYOTA
Corolla XEI → COROLLA XEI
```

---

## Arquivos relacionados

Schema formal:

```text
skill/schemas/canonical_irpf_2026.json
```

Validação canônica:

```text
tools/validate.py
```

Geração do JSON canônico:

```text
tools/build_canonical_json.py
```

Consolidação:

```text
tools/pipeline_batch.py
```

Relatório:

```text
tools/report.py
```

---

## Decisões técnicas

### 1. JSON antes de `.DEC`

O projeto sempre gera JSON canônico antes de qualquer `.DEC`.

Motivo:

- OCR pode errar;
- usuário precisa revisar;
- `.DEC` exige compatibilidade rígida;
- JSON é legível e versionável.

### 2. Valores em centavos

Evita erros com `float`.

### 3. Revisão humana obrigatória

O relatório humano é parte obrigatória do fluxo.

### 4. Estrutura versionada

O campo:

```json
"$schema": "irpf-2026-v1"
```

permite evoluir o formato no futuro.

### 5. `tipo_bem`

A partir do suporte a veículos, todo item em `bens[]` deve declarar:

```text
tipo_bem
```

Valores atuais:

```text
IMOVEL
VEICULO
```

Isso permite aplicar validações e relatórios específicos para cada tipo de bem.

---

## Próximas extensões

Próximas seções planejadas:

```text
dividas[]
dependentes[]
rendimentos isentos
rendimentos exclusivos
renda variável
ganho de capital
```
