# Códigos de Pagamentos — IRPF

Este arquivo documenta os códigos de pagamentos usados pelo projeto.

Nesta fase, a referência ainda é mínima e cobre apenas os códigos já suportados pelo pipeline.

## Códigos atualmente suportados

| Código | Descrição no projeto | Origem no pipeline | Destino no JSON canônico |
|---|---|---|---|
| 10 | Médicos no Brasil | `recibo_medico` | `pagamentos[]` |
| 26 | Planos de saúde no Brasil | `plano_saude` | `pagamentos[]` |

---

## Código 10 — Médicos no Brasil

Usado para recibos médicos.

Documento de origem:

```json
{
  "document_type": "recibo_medico"
}