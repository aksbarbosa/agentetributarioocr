# Tipos de Documentos Suportados

Este arquivo documenta os tipos de documentos que a skill reconhece atualmente.

Cada arquivo de extração deve conter um campo:

```json
{
  "document_type": "..."
}
```

O valor de `document_type` define:

- quais campos são obrigatórios;
- qual validador será usado;
- como o documento será convertido para JSON canônico;
- em qual seção do JSON canônico os dados serão inseridos.

---

## Visão geral

| `document_type` | Documento | Destino no JSON canônico | Status |
|---|---|---|---|
| `informe_rendimentos_pj` | Informe de rendimentos de pessoa jurídica | `rendimentos.tributaveis_pj[]` | Implementado |
| `recibo_medico` | Recibo médico | `pagamentos[]` | Implementado |
| `plano_saude` | Informe de plano de saúde | `pagamentos[]` | Implementado |
| `bem_imovel` | Bem imóvel | `bens[]` | Implementado |
| `bem_veiculo` | Bem veículo | `bens[]` | Implementado |

---

# 1. `informe_rendimentos_pj`

Representa informe de rendimentos emitido por pessoa jurídica.

## Campos obrigatórios

```text
cpf_declarante
nome_declarante
data_nascimento
cnpj_pagador
nome_pagador
rendimento_total
previdencia_oficial
decimo_terceiro
irrf
irrf_13
```

## Destino no JSON canônico

```json
{
  "rendimentos": {
    "tributaveis_pj": []
  }
}
```

## Exemplo de saída canônica

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

---

# 2. `recibo_medico`

Representa recibo médico individual.

## Campos obrigatórios

```text
cpf_declarante
nome_declarante
data_nascimento
cpf_cnpj_prestador
nome_prestador
valor_pago
data_pagamento
descricao
```

## Destino no JSON canônico

```json
{
  "pagamentos": []
}
```

## Código de pagamento

```text
10
```

## Exemplo de saída canônica

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

---

# 3. `plano_saude`

Representa informe anual de plano de saúde.

## Campos obrigatórios

```text
cpf_declarante
nome_declarante
data_nascimento
cnpj_operadora
nome_operadora
valor_pago
valor_nao_dedutivel
descricao
```

## Destino no JSON canônico

```json
{
  "pagamentos": []
}
```

## Código de pagamento

```text
26
```

## Exemplo de saída canônica

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

---

# 4. `bem_imovel`

Representa um bem imóvel, como apartamento, casa, terreno ou outro imóvel declarado em bens e direitos.

Nesta fase, o projeto suporta o caso simples de apartamento residencial.

## Campos obrigatórios

```text
cpf_declarante
nome_declarante
data_nascimento
codigo_bem
grupo_bem
descricao
valor_anterior
valor_atual
cep
logradouro
numero
bairro
municipio
uf
iptu
matricula
data_aquisicao
```

## Destino no JSON canônico

```json
{
  "bens": []
}
```

## Grupo, código e tipo atuais

```text
tipo_bem = IMOVEL
grupo_bem = 01
codigo_bem = 11
```

Nesta fase:

```text
grupo_bem 01 → bens imóveis
codigo_bem 11 → apartamento
```

## Exemplo de saída canônica

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

---

# 5. `bem_veiculo`

Representa um bem veículo, como automóvel ou outro veículo automotor terrestre declarado em bens e direitos.

Nesta fase, o projeto suporta o caso simples de automóvel.

## Campos obrigatórios

```text
cpf_declarante
nome_declarante
data_nascimento
grupo_bem
codigo_bem
descricao
valor_anterior
valor_atual
renavam
placa
marca
modelo
ano_fabricacao
data_aquisicao
```

## Destino no JSON canônico

```json
{
  "bens": []
}
```

## Grupo, código e tipo atuais

```text
tipo_bem = VEICULO
grupo_bem = 02
codigo_bem = 01
```

Nesta fase:

```text
grupo_bem 02 → bens móveis
codigo_bem 01 → veículo automotor terrestre
```

## Exemplo de saída canônica

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

---

## Estrutura comum de campo extraído

Todo campo dentro de `fields` deve seguir este formato:

```json
{
  "value": "valor extraído",
  "confidence": "high",
  "source_hint": "Página 1, campo X"
}
```

Valores permitidos para `confidence`:

```text
high
medium
low
```

---

## Regras de revisão

Campos com:

```json
{
  "confidence": "low"
}
```

devem gerar pendência de revisão humana.

Campos ausentes devem gerar erro na validação da extração.

---

## Arquivos relacionados

Validação de extrações:

```text
tools/validate_extracted.py
```

Conversão para JSON canônico:

```text
tools/build_canonical_json.py
```

Pipeline individual:

```text
tools/pipeline_from_extracted.py
```

Pipeline em lote:

```text
tools/pipeline_batch.py
```

Schemas relacionados:

```text
skill/schemas/extracted_informe_pj.json
skill/schemas/extracted_recibo_medico.json
skill/schemas/extracted_plano_saude.json
skill/schemas/extracted_bem_imovel.json
skill/schemas/extracted_bem_veiculo.json
```

---

## Próximos tipos planejados

Tipos que podem ser adicionados futuramente:

| `document_type` | Documento | Destino provável |
|---|---|---|
| `informe_bancario` | Informe de banco | `bens[]` / rendimentos |
| `previdencia_privada` | Informe PGBL/VGBL | `pagamentos[]` / bens |
| `recibo_educacao` | Escola, faculdade, curso | `pagamentos[]` |
| `aluguel_recebido` | Aluguel recebido | `rendimentos` |
| `dependente` | Documento de dependente | `dependentes[]` |
