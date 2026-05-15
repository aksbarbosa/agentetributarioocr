# IRPF OCR DEC

Projeto experimental para construção de uma skill/agente capaz de auxiliar na organização inicial de dados para Declaração de Imposto de Renda Pessoa Física brasileira a partir de documentos brutos, textos extraídos, PDFs pesquisáveis, PDFs escaneados, imagens com OCR e extrações estruturadas.

A ideia central é transformar documentos fiscais em um JSON canônico revisável e, futuramente, gerar um arquivo `.DEC` experimental importável no PGD oficial da Receita Federal.

---

## Aviso importante

Este projeto não substitui contador, revisão humana, PGD oficial da Receita Federal ou responsabilidade do contribuinte.

O fluxo correto deve sempre preservar uma etapa de conferência humana:

```text
documento bruto
    ↓
extração de texto ou OCR
    ↓
classificação
    ↓
pré-triagem
    ↓
extração estruturada
    ↓
validação da extração
    ↓
promoção segura
    ↓
revisão humana
    ↓
JSON canônico
    ↓
validação canônica
    ↓
relatório humano
    ↓
geração futura do .DEC
```

---

## Estado atual do projeto

O projeto já possui uma base funcional para processamento determinístico e um fluxo real inicial a partir de arquivos brutos.

Atualmente existe suporte para:

- classificador simples de documentos;
- simulador local de agente individual;
- simulador local de agente em lote;
- pré-triagem de documentos;
- scanner de documentos brutos em `inputs/raw/`;
- extração de texto de `.txt`;
- extração de texto de PDF pesquisável com `pypdf`;
- OCR de imagem com Tesseract via `pytesseract`;
- pré-processamento simples de imagem para OCR;
- fallback OCR para PDF escaneado usando `pdf2image` + Poppler + Tesseract;
- extração estruturada heurística para os 5 tipos principais do pipeline;
- extração estruturada em lote;
- validação de extrações estruturadas;
- promoção segura de extrações válidas e sem `requires_review`;
- pipeline canônico a partir de `inputs/extracted/`;
- validação canônica;
- relatório humano;
- limpeza de outputs conhecidos;
- checagem de desenvolvimento integrada;
- testes automatizados.

Ainda não possui:

- OCR robusto para todos os cenários reais;
- revisão humana assistida completa;
- interface de correção;
- integração final com Agno;
- geração `.DEC`;
- transmissão de declaração;
- parser reverso `.DEC`;
- cálculo completo de imposto.

---

## Estrutura geral

```text
irpf_ocr_dec/
├── config/
│   └── project_config.json
├── inputs/
│   ├── raw/
│   └── extracted/
├── outputs/
│   ├── extracted_text/
│   ├── structured_extractions/
│   └── promoted_extractions/
├── skill/
│   ├── SKILL.md
│   ├── instructions.md
│   └── references/
├── tests/
│   ├── fixtures/
│   ├── run_tests.py
│   └── unit/
├── tools/
└── requirements.txt
```

---

## Pastas principais

### `inputs/raw/`

Entrada de documentos brutos.

Pode conter, por exemplo:

```text
.txt
.pdf
.png
.jpg
.jpeg
.tif
.tiff
```

Esses arquivos são usados pelo fluxo real:

```bash
python3 tools/run_raw_flow.py
```

### `outputs/extracted_text/`

Recebe textos extraídos de arquivos brutos.

### `outputs/structured_extractions/`

Recebe JSONs estruturados gerados automaticamente a partir dos textos extraídos.

Essa pasta contém resultados automáticos e ainda pode incluir itens que exigem revisão.

### `outputs/promoted_extractions/`

Área segura de promoção.

Contém somente extrações estruturadas válidas e sem `requires_review`.

Esses arquivos ainda não são copiados automaticamente para `inputs/extracted/`.

### `inputs/extracted/`

Entrada oficial do pipeline canônico.

Deve conter apenas JSONs estruturados revisados, válidos e seguros para consolidação.

---

## Instalação

### 1. Criar ambiente virtual

```bash
cd ~/Documents/irpf_ocr_dec

python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências Python

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

O `requirements.txt` atual deve conter:

```text
pypdf
pillow
pytesseract
pdf2image
```

### 3. Instalar Tesseract no macOS

```bash
brew install tesseract
brew install tesseract-lang
```

Conferir:

```bash
tesseract --version
```

### 4. Instalar Poppler no macOS

O `pdf2image` usa utilitários do Poppler para converter páginas de PDF em imagens.

```bash
brew install poppler
```

Conferir:

```bash
pdftoppm -h
```

### 5. Testar dependências

```bash
python3 - <<'PY'
import pypdf
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

print("Dependências Python OK")
PY
```

---

## Documentos suportados atualmente

| Documento | `document_type` | Destino canônico |
|---|---|---|
| Informe de rendimentos PJ | `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| Recibo médico | `recibo_medico` | `pagamentos[]` |
| Plano de saúde | `plano_saude` | `pagamentos[]` |
| Bem imóvel | `bem_imovel` | `bens[]` |
| Bem veículo | `bem_veiculo` | `bens[]` |

A extração estruturada automática a partir de texto já cobre os principais tipos usados pelo pipeline canônico:

```text
recibo_medico
informe_rendimentos_pj
plano_saude
bem_veiculo
bem_imovel
```

Essas extrações são heurísticas, determinísticas e ainda exigem revisão humana antes de uso real na declaração.

---

## Fluxo real a partir de documentos brutos

O projeto possui um fluxo real inicial para processar arquivos em `inputs/raw/`.

Comando principal:

```bash
python3 tools/run_raw_flow.py
```

Esse comando executa:

```text
inputs/raw/
    ↓
tools/scan_raw_inputs.py
    ↓
tools/extract_text.py
    ↓
outputs/extracted_text/
    ↓
tools/preflight_documents.py
    ↓
tools/extract_structured_batch.py
    ↓
outputs/structured_extractions/
    ↓
tools/validate_extracted.py
    ↓
tools/promote_structured_extractions.py
    ↓
outputs/promoted_extractions/
```

Etapas do fluxo:

1. escaneia arquivos brutos;
2. extrai texto de `.txt`, PDF pesquisável, imagem via OCR e PDF escaneado via OCR por página;
3. faz pré-triagem dos textos extraídos;
4. gera extrações estruturadas em lote;
5. valida os JSONs estruturados;
6. promove somente extrações válidas e sem `requires_review` para `outputs/promoted_extractions/`.

A pasta `outputs/promoted_extractions/` é uma área segura de revisão. Os arquivos nela ainda não são copiados automaticamente para `inputs/extracted/`.

---

## Fluxos individuais

### Scanner de documentos brutos

```bash
python3 tools/scan_raw_inputs.py inputs/raw
python3 tools/scan_raw_inputs.py inputs/raw --json
```

Gera:

```text
outputs/raw-inputs-manifest.json
outputs/raw-inputs-manifest.report.md
```

### Extração de texto e OCR

```bash
python3 tools/extract_text.py inputs/raw
python3 tools/extract_text.py inputs/raw --json
```

Gera:

```text
outputs/extract-text.json
outputs/extract-text.report.md
outputs/extracted_text/
```

Comportamento atual:

| Tipo | Comportamento |
|---|---|
| `.txt` | lê texto diretamente |
| PDF pesquisável | tenta extrair texto com `pypdf` |
| PDF escaneado | tenta converter páginas em imagens com `pdf2image` e aplicar OCR |
| imagem | tenta OCR com Tesseract |
| arquivo vazio | marca como `empty` |
| extensão não suportada | marca como `unsupported` |
| PDF/imagem inválido | marca como `requires_ocr` ou falha tratada com aviso |

### Classificação de texto

```bash
python3 tools/classify_document.py outputs/extracted_text/teste_recibo.txt
python3 tools/classify_document.py outputs/extracted_text/teste_recibo.txt --json
```

Retorna:

```text
document_type
label
confidence
scores
matched_keywords
```

### Pré-triagem

```bash
python3 tools/preflight_documents.py outputs/extracted_text
python3 tools/preflight_documents.py outputs/extracted_text --json
```

Gera:

```text
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

Status possíveis:

```text
ready
blocked
```

### Extração estruturada individual

```bash
python3 tools/extract_structured_from_text.py outputs/extracted_text/teste_recibo.txt --json
```

Salvar JSON estruturado:

```bash
python3 tools/extract_structured_from_text.py \
  outputs/extracted_text/teste_recibo.txt \
  outputs/manual_extracted/teste_recibo.json
```

Exemplos:

```bash
python3 tools/extract_structured_from_text.py \
  outputs/extracted_text/informe_pj_teste.txt \
  outputs/manual_extracted/informe_pj_teste.json

python3 tools/extract_structured_from_text.py \
  outputs/extracted_text/plano_saude_teste.txt \
  outputs/manual_extracted/plano_saude_teste.json

python3 tools/extract_structured_from_text.py \
  outputs/extracted_text/bem_veiculo_teste.txt \
  outputs/manual_extracted/bem_veiculo_teste.json

python3 tools/extract_structured_from_text.py \
  outputs/extracted_text/bem_imovel_teste.txt \
  outputs/manual_extracted/bem_imovel_teste.json
```

### Extração estruturada em lote

```bash
python3 tools/extract_structured_batch.py outputs/extracted_text
python3 tools/extract_structured_batch.py outputs/extracted_text --json
```

Gera:

```text
outputs/structured_extractions/
outputs/structured-extractions-batch.json
outputs/structured-extractions-batch.report.md
```

Atualmente o lote salva automaticamente estes tipos:

```text
recibo_medico
informe_rendimentos_pj
plano_saude
bem_veiculo
bem_imovel
```

Tipos desconhecidos ou ainda não implementados são marcados como `requires_review`.

### Validação das extrações estruturadas

Validar arquivo individual:

```bash
python3 tools/validate_extracted.py outputs/structured_extractions/testemedic.json
```

Validar todos os JSONs gerados:

```bash
for f in outputs/structured_extractions/*.json; do
  echo "Validando $f"
  python3 tools/validate_extracted.py "$f"
done
```

### Promoção segura

A promoção segura copia apenas JSONs válidos e sem `requires_review`.

Teste em pasta segura:

```bash
python3 tools/promote_structured_extractions.py \
  outputs/structured_extractions \
  outputs/promoted_test \
  outputs/promote-structured-extractions.json \
  outputs/promote-structured-extractions.report.md
```

Uso padrão:

```bash
python3 tools/promote_structured_extractions.py
```

Por padrão:

```text
origem: outputs/structured_extractions/
destino: inputs/extracted/
```

Recomendação atual: preferir promoção para `outputs/promoted_extractions/` via `run_raw_flow.py`, revisar os arquivos e só depois decidir se devem entrar em `inputs/extracted/`.

---

## Pipeline canônico

O pipeline canônico ainda usa como entrada oficial:

```text
inputs/extracted/
```

Rodar:

```bash
python3 tools/run_project.py
```

Gera:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
```

Esse pipeline:

1. lê extrações estruturadas;
2. valida extrações;
3. normaliza dados;
4. constrói JSON canônico parcial;
5. consolida;
6. valida o JSON consolidado;
7. gera relatório humano.

---

## Checagem de desenvolvimento

Rodar:

```bash
python3 tools/dev_check.py
```

Executa uma checagem integrada do estado do projeto.

---

## Limpeza de outputs

Rodar:

```bash
python3 tools/clean_outputs.py
```

Remove outputs conhecidos como:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
outputs/agent-decision.json
outputs/agent-decisions.json
outputs/agent-decisions.report.md
outputs/preflight-documents.json
outputs/preflight-documents.report.md
outputs/raw-inputs-manifest.json
outputs/raw-inputs-manifest.report.md
outputs/extract-text.json
outputs/extract-text.report.md
outputs/structured-extractions-batch.json
outputs/structured-extractions-batch.report.md
outputs/promote-structured-extractions.json
outputs/promote-structured-extractions.report.md
```

Por segurança, algumas pastas de revisão não são apagadas automaticamente, como:

```text
outputs/promoted_extractions/
outputs/structured_extractions/
outputs/extracted_text/
```

---

## Testes

Rodar todos os testes:

```bash
python3 tests/run_tests.py
```

Rodar checagem completa:

```bash
python3 tools/dev_check.py
```

Testes relevantes atuais:

```text
tests/unit/test_normalize.py
tests/unit/test_validate.py
tests/unit/test_validate_config.py
tests/unit/test_validate_extracted.py
tests/unit/test_build_canonical_json.py
tests/unit/test_pipeline_batch.py
tests/unit/test_report.py
tests/unit/test_clean_outputs.py
tests/unit/test_scan_raw_inputs.py
tests/unit/test_extract_text.py
tests/unit/test_extract_structured_from_text.py
tests/unit/test_extract_structured_batch.py
tests/unit/test_promote_structured_extractions.py
tests/unit/test_run_project.py
tests/unit/test_run_raw_flow.py
tests/unit/test_classify_document.py
tests/unit/test_agent_simulator.py
tests/unit/test_agent_batch_simulator.py
tests/unit/test_preflight_documents.py
```

---

## Comandos úteis

### Rodar fluxo real completo

```bash
python3 tools/run_raw_flow.py
```

### Rodar pipeline canônico

```bash
python3 tools/run_project.py
```

### Rodar testes

```bash
python3 tests/run_tests.py
```

### Rodar checagem de desenvolvimento

```bash
python3 tools/dev_check.py
```

### Ver status Git

```bash
git status
```

### Commit padrão

```bash
git add .
git commit -m "Mensagem objetiva"
git push
```

---

## Estado atual em termos de capacidade

Já funciona:

```text
TXT real                         → extração de texto
PDF pesquisável                  → extração com pypdf
Imagem/print                     → OCR com Tesseract
PDF escaneado                    → fallback OCR por página com pdf2image + Tesseract
Texto extraído                   → classificação
Recibo médico                    → extração estruturada heurística
Informe de rendimentos PJ        → extração estruturada heurística
Plano de saúde                   → extração estruturada heurística
Bem veículo                      → extração estruturada heurística
Bem imóvel                       → extração estruturada heurística
JSON estruturado                 → validação
Extração sem revisão             → promoção segura
Pipeline canônico                → consolidação a partir de inputs/extracted/
```

Ainda precisa melhorar:

```text
OCR de fotos ruins
pré-processamento mais robusto de imagem
PDF escaneado multipágina em cenários reais variados
extração estruturada mais robusta para documentos reais
revisão humana assistida
integração final com Agno
geração .DEC
```

---

## Próximos passos técnicos recomendados

Prioridade recomendada:

1. criar etapa de revisão humana assistida para `outputs/promoted_extractions/`;
2. criar ferramenta para copiar extrações revisadas para `inputs/extracted/`;
3. tornar `run_raw_flow.py` configurável por flags;
4. melhorar OCR com pré-processamento mais robusto;
5. testar PDF escaneado multipágina real;
6. robustecer extrações heurísticas com mais padrões reais;
7. integrar com Agno;
8. estudar formato `.DEC`.

---

## Observação sobre arquivos reais

Não coloque documentos reais sensíveis no Git.

Evite versionar:

```text
outputs/
inputs/raw/
documentos pessoais reais
prints com CPF real
```

Use dados fictícios para testes versionados.
