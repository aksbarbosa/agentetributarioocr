# Códigos de Bens e Direitos — IRPF

Este arquivo documenta os códigos de bens e direitos usados pelo projeto.

Nesta fase, a referência ainda cobre apenas os códigos já suportados pelo pipeline.

---

## Estrutura geral

No JSON canônico, bens são armazenados em:

```json
"bens": []
```

Cada bem possui campos comuns:

```json
{
  "tipo_bem": "IMOVEL",
  "grupo_bem": "01",
  "codigo_bem": "11",
  "descricao": "...",
  "valor_anterior": 0,
  "valor_atual": 0
}
```

O campo `tipo_bem` é usado internamente pelo projeto para aplicar validações e relatório específicos.

Valores atuais:

```text
IMOVEL
VEICULO
```

---

## Códigos atualmente suportados

| Grupo | Código | Tipo interno | Descrição no projeto | Origem no pipeline | Destino no JSON canônico |
|---|---|---|---|---|---|
| 01 | 11 | `IMOVEL` | Apartamento | `bem_imovel` | `bens[]` |
| 02 | 01 | `VEICULO` | Veículo automotor terrestre | `bem_veiculo` | `bens[]` |

---

# Grupo 01 — Bens Imóveis

O grupo `01` representa bens imóveis.

Nesta fase, o projeto suporta:

| Grupo | Código | Descrição |
|---|---|---|
| 01 | 11 | Apartamento |

---

## Código 11 — Apartamento

Usado para representar apartamento residencial.

Documento de origem atual:

```json
{
  "document_type": "bem_imovel"
}
```

Exemplo de bem canônico:

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

## Campos específicos de imóvel

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `endereco.cep` | string | 8 dígitos | CEP do imóvel |
| `endereco.logradouro` | string | texto normalizado | Rua, avenida etc. |
| `endereco.numero` | string | texto | Número do imóvel |
| `endereco.bairro` | string | texto normalizado | Bairro |
| `endereco.municipio` | string | texto normalizado | Município |
| `endereco.uf` | string | 2 letras | Unidade federativa |
| `iptu` | string | dígitos | Número do cadastro municipal/IPTU |
| `matricula` | string | dígitos | Matrícula do imóvel |

---

# Grupo 02 — Bens Móveis

O grupo `02` representa bens móveis.

Nesta fase, o projeto suporta:

| Grupo | Código | Descrição |
|---|---|---|
| 02 | 01 | Veículo automotor terrestre |

---

## Código 01 — Veículo automotor terrestre

Usado para representar automóvel ou outro veículo automotor terrestre.

Documento de origem atual:

```json
{
  "document_type": "bem_veiculo"
}
```

Exemplo de bem canônico:

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

## Campos específicos de veículo

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `renavam` | string | dígitos | Código RENAVAM |
| `placa` | string | texto normalizado | Placa do veículo |
| `marca` | string | texto normalizado | Marca do veículo |
| `modelo` | string | texto normalizado | Modelo do veículo |
| `ano_fabricacao` | string | 4 dígitos | Ano de fabricação |

---

## Campos comuns de bens

| Campo | Tipo | Formato | Observação |
|---|---|---|---|
| `tipo_bem` | string | `IMOVEL` ou `VEICULO` | Tipo interno do bem |
| `grupo_bem` | string | 2 dígitos | Grupo do bem |
| `codigo_bem` | string | 2 dígitos | Código específico do bem |
| `descricao` | string | texto normalizado | Descrição detalhada do bem |
| `valor_anterior` | integer | centavos | Valor em 31/12 do ano anterior |
| `valor_atual` | integer | centavos | Valor em 31/12 do ano-calendário |
| `data_aquisicao` | string | `DDMMAAAA` | Data de aquisição |
| `beneficiario_tipo` | string | `T` ou `D` | Titular ou dependente |

---

## Regras atuais de validação

O arquivo:

```text
tools/validate.py
```

valida atualmente campos comuns de bens:

- `tipo_bem` obrigatório;
- `tipo_bem` igual a `IMOVEL` ou `VEICULO`;
- `grupo_bem` obrigatório;
- `grupo_bem` com 2 dígitos;
- `codigo_bem` obrigatório;
- `codigo_bem` com 2 dígitos;
- descrição obrigatória;
- `valor_anterior` não negativo;
- `valor_atual` não negativo;
- data de aquisição em `DDMMAAAA`;
- `beneficiario_tipo` igual a `T` ou `D`.

Para imóveis, valida também:

- endereço como objeto;
- CEP com 8 dígitos;
- logradouro obrigatório;
- município obrigatório;
- UF válida;
- IPTU ausente como aviso;
- matrícula ausente como aviso.

Para veículos, valida também:

- RENAVAM obrigatório;
- RENAVAM com quantidade incomum de dígitos como aviso;
- placa obrigatória;
- placa com tamanho incomum como aviso;
- marca obrigatória;
- modelo obrigatório;
- ano de fabricação obrigatório;
- ano de fabricação com 4 dígitos.

---

## Observações importantes

### Valores monetários

Os valores são sempre armazenados em centavos.

Exemplos:

```text
R$ 250.000,00 → 25000000
R$ 80.000,00 → 8000000
```

### Descrição

A descrição do bem deve ser suficientemente clara para revisão humana.

Exemplos:

```text
APARTAMENTO RESIDENCIAL LOCALIZADO NA RUA DAS FLORES, NUMERO 123, BAIRRO CENTRO, SAO PAULO SP
AUTOMOVEL MARCA TOYOTA, MODELO COROLLA XEI, ANO 2020, PLACA ABC1D23
```

### Revisão humana

Se qualquer campo vier com baixa confiança, deve aparecer em:

```json
"requires_review": []
```

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

## Próximos códigos planejados

Códigos que podem ser adicionados futuramente:

| Grupo | Código | Possível uso |
|---|---|---|
| 01 | 12 | Casa |
| 01 | 13 | Terreno |
| 01 | 14 | Galpão |
| 02 | 02 | Aeronave |
| 02 | 03 | Embarcação |
| 04 | 01 | Aplicação financeira |
| 06 | 01 | Conta corrente |
| 06 | 02 | Poupança |

Antes de adicionar novos códigos, o projeto deve atualizar:

```text
skill/references/codigos_bens.md
skill/references/tipos_documentos.md
skill/references/json_canonico.md
tools/validate_extracted.py
tools/build_canonical_json.py
tools/validate.py
tools/report.py, se necessário
tests/
```

---

## Decisão técnica

Neste estágio, a lista de códigos de bens é propositalmente pequena.

O projeto só deve aceitar e documentar códigos que ele realmente sabe:

- extrair;
- converter;
- validar;
- consolidar;
- exibir no relatório;
- testar.
