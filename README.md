# IRPF OCR DEC

Projeto experimental para transformar documentos fiscais em dados estruturados revisáveis, consolidar essas informações em um JSON canônico para IRPF e preparar uma exportação experimental pré-DEC.

> **Aviso importante:** este projeto ainda não gera um `.DEC` oficial compatível com o PGD da Receita Federal. A exportação atual é experimental e serve apenas para estudo de mapeamento e evolução futura.

---

## Objetivo

Criar um fluxo local, determinístico e revisável para auxiliar na organização de documentos usados na declaração de IRPF.

O fluxo atual cobre:

```text
documentos brutos
→ extração de texto/OCR
→ classificação documental
→ pré-triagem
→ extração estruturada
→ validação
→ promoção segura
→ revisão assistida
→ pacote de revisão manual
→ aplicação de correções humanas
→ aprovação segura
→ JSON canônico
→ relatório humano
→ exportação experimental pré-DEC
```

---

## Status atual

```text
MVP local funcional: avançado
Fluxo raw-to-canonical: funcional
Revisão humana assistida: funcional
Aplicação de correções manuais: funcional
Estratégia OCR configurável: funcional
Seleção de melhor OCR: funcional
Interface unificada: funcional
Makefile com atalhos: funcional
GitHub Actions CI: funcional/em validação
Exportação experimental pré-DEC: funcional
Geração .DEC oficial: ainda não implementada
```

O sistema bloqueia avanço automático quando encontra:

```text
CPF inválido
CNPJ inválido
CPF/CNPJ inválido
campos ausentes
campos de baixa confiança
documentos desconhecidos
documentos que exigem OCR/revisão manual
JSON canônico inválido
```

---

## Interface principal

O projeto possui uma interface unificada:

```bash
python3 tools/irpf_ocr.py <comando>
```

Comandos principais:

```bash
python3 tools/irpf_ocr.py setup
python3 tools/irpf_ocr.py status
python3 tools/irpf_ocr.py project-status
python3 tools/irpf_ocr.py run
python3 tools/irpf_ocr.py continue
python3 tools/irpf_ocr.py check
```

### Significado dos comandos

```text
setup           configura o projeto localmente, instala hooks e roda checagens
status          mostra a estratégia OCR configurada
project-status  mostra o estado dos outputs e o próximo passo provável
run             executa o fluxo definido em config/ocr_config.json
continue        continua depois da revisão manual conforme a estratégia OCR
check           roda validações e testes do projeto
```

---

## Atalhos com Makefile

Também é possível usar:

```bash
make setup
make status
make project-status
make run
make continue
make check
make test
make safety
```

Equivalências principais:

```text
make setup          → python3 tools/irpf_ocr.py setup
make status         → python3 tools/irpf_ocr.py status
make project-status → python3 tools/irpf_ocr.py project-status
make run            → python3 tools/irpf_ocr.py run
make continue       → python3 tools/irpf_ocr.py continue
make check          → python3 tools/irpf_ocr.py check
make test           → python3 tests/run_tests.py
make safety         → python3 tools/check_repo_safety.py
```

---

## Uso recomendado

Depois de clonar o projeto:

```bash
cd ~/Documents/irpf_ocr_dec
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 tools/irpf_ocr.py setup
```

No uso diário:

```bash
python3 tools/irpf_ocr.py status
python3 tools/irpf_ocr.py run
```

Se o fluxo parar para revisão humana:

```bash
python3 tools/irpf_ocr.py continue
```

Para checagem geral:

```bash
python3 tools/irpf_ocr.py check
```

---

## Configuração OCR

A estratégia OCR é controlada por:

```text
config/ocr_config.json
```

Estratégias aceitas:

```text
normal
prepared
best
```

Mapeamento:

```text
ocr_strategy = normal   → tools/run_mvp_flow.py
ocr_strategy = prepared → tools/run_prepared_raw_flow.py
ocr_strategy = best     → tools/run_best_mvp_flow.py
```

Continuação após revisão:

```text
normal → tools/continue_after_manual_review.py
best   → tools/continue_after_best_manual_review.py
```

A estratégia `prepared` ainda é experimental e não possui continuação canônica completa.

Validar a configuração OCR:

```bash
python3 tools/validate_ocr_config.py
```

Ver status da estratégia OCR:

```bash
python3 tools/ocr_strategy_status.py
```

---

## Exemplo de `config/ocr_config.json`

```json
{
  "ocr_strategy": "best",
  "paths": {
    "raw_input_dir": "inputs/raw",
    "prepared_input_dir": "outputs/raw_prepared_for_ocr",
    "extracted_text_dir": "outputs/extracted_text",
    "extracted_text_prepared_dir": "outputs/extracted_text_prepared",
    "extracted_text_best_dir": "outputs/extracted_text_best"
  },
  "preprocessing": {
    "enabled": true,
    "scale_factor": 2,
    "contrast_factor": 1.8,
    "sharpness_factor": 1.5,
    "binarization_threshold": 180
  },
  "selection": {
    "method": "longest_text",
    "prefer_original_on_tie": true
  },
  "safety": {
    "allow_partial_preprocessing_errors": true,
    "allow_preflight_failure": true,
    "require_manual_review_for_invalid_identifiers": true
  }
}
```

---

## Tipos de documento suportados

```text
recibo_medico
plano_saude
informe_rendimentos_pj
bem_imovel
bem_veiculo
```

Documentos desconhecidos são bloqueados antes de entrar no fluxo canônico.

---

## Estrutura principal

```text
irpf_ocr_dec/
├── .github/
│   └── workflows/
│       └── ci.yml
├── config/
│   ├── project_config.json
│   └── ocr_config.json
├── inputs/
│   ├── raw/
│   ├── raw_ignored/
│   └── extracted/
├── outputs/
│   └── .gitkeep
├── scripts/
│   └── git-hooks/
│       └── pre-commit
├── tools/
├── tests/
│   └── unit/
├── skill/
│   └── SKILL.md
├── Makefile
├── README.md
├── DOCUMENTACAO.md
└── CHANGELOG.md
```

---

## Pastas importantes

### `inputs/raw/`

Pasta local para documentos brutos:

```text
PDF pesquisável
PDF escaneado
imagem PNG/JPG
TXT
```

Essa pasta deve ser ignorada pelo Git.

### `inputs/raw_ignored/`

Arquivos removidos do fluxo por estarem vazios, corrompidos ou fora do escopo.

### `inputs/extracted/`

JSONs estruturados manuais ou fixtures já prontos para o pipeline canônico.

### `outputs/`

Relatórios, JSONs intermediários, textos extraídos, pacotes de revisão e exportações.

Essa pasta deve ser ignorada pelo Git, exceto `outputs/.gitkeep`.

---

## Scripts principais

### Interface, configuração e status

```text
tools/irpf_ocr.py
tools/setup_project.py
tools/project_status.py
tools/ocr_strategy_status.py
tools/run_ocr_strategy.py
tools/continue_after_ocr_strategy_review.py
tools/validate_config.py
tools/validate_ocr_config.py
```

### Segurança do repositório

```text
tools/check_repo_safety.py
tools/install_git_hooks.py
scripts/git-hooks/pre-commit
```

### OCR e preparação

```text
tools/extract_text.py
tools/preprocess_raw_images.py
tools/prepare_raw_for_ocr.py
tools/run_prepared_raw_flow.py
tools/compare_ocr_outputs.py
tools/select_best_ocr_outputs.py
tools/run_best_ocr_flow.py
```

### Classificação, triagem e extração estruturada

```text
tools/classify_document.py
tools/preflight_documents.py
tools/extract_structured_from_text.py
tools/extract_structured_batch.py
```

### Validação, promoção e revisão

```text
tools/validate_extracted.py
tools/promote_structured_extractions.py
tools/review_promoted_extractions.py
tools/generate_manual_review_pack.py
tools/apply_manual_review_pack.py
tools/approve_promoted_extractions.py
```

### Fluxos completos

```text
tools/run_raw_flow.py
tools/run_mvp_flow.py
tools/continue_after_manual_review.py
tools/run_best_mvp_flow.py
tools/continue_after_best_manual_review.py
```

### Pipeline canônico e exportação

```text
tools/run_project.py
tools/pipeline_batch.py
tools/build_canonical_json.py
tools/report.py
tools/export_dec_experimental.py
```

### Desenvolvimento

```text
tools/dev_check.py
tools/clean_outputs.py
tests/run_tests.py
```

---

## Instalação

No macOS:

```bash
cd ~/Documents/irpf_ocr_dec
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Se for usar OCR com Tesseract:

```bash
brew install tesseract
brew install tesseract-lang
```

Depois:

```bash
python3 tools/setup_project.py
```

ou:

```bash
python3 tools/irpf_ocr.py setup
```

---

## Checagem de desenvolvimento

Rodar testes:

```bash
python3 tests/run_tests.py
```

Rodar checagem completa:

```bash
python3 tools/dev_check.py
```

O `dev_check.py` deve executar:

```text
validate_config.py
validate_ocr_config.py
tests/run_tests.py
check_repo_safety.py
```

---

## Segurança do repositório

O projeto possui proteção contra commit acidental de documentos fiscais, imagens, PDFs, outputs e `.DEC`.

Checagem manual:

```bash
python3 tools/check_repo_safety.py
```

Instalar hook local:

```bash
python3 tools/install_git_hooks.py
```

O hook versionado fica em:

```text
scripts/git-hooks/pre-commit
```

Ele é copiado para:

```text
.git/hooks/pre-commit
```

Arquivos e pastas que não devem ser commitados:

```text
inputs/raw/
inputs/raw_test_*/
inputs/raw_ignored/
inputs/private/
inputs/real/
outputs/
*.pdf
*.jpg
*.jpeg
*.png
*.tif
*.tiff
*.webp
*.dec
*.DEC
```

---

## CI / GitHub Actions

O projeto possui workflow de CI em:

```text
.github/workflows/ci.yml
```

A cada `push` na branch `main` e a cada `pull_request`, o GitHub Actions executa:

```bash
python tools/validate_config.py config/project_config.json
python tools/validate_ocr_config.py
python tools/check_repo_safety.py
python tests/run_tests.py
python tools/dev_check.py
```

O objetivo do CI é garantir que:

```text
configurações continuam válidas
testes unitários continuam passando
arquivos sensíveis não foram rastreados
checagem de desenvolvimento continua íntegra
```

---

## Fluxo rápido com JSONs estruturados

Usa:

```text
inputs/extracted/
```

Rodar:

```bash
python3 tools/run_project.py
```

Saídas:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
```

Validar JSON consolidado:

```bash
python3 -m json.tool outputs/irpf-consolidado.json > /tmp/irpf_ok.json
```

---

## Fluxo raw normal

```bash
python3 tools/run_raw_flow.py
```

Fluxo:

```text
inputs/raw/
→ extract_text.py
→ preflight_documents.py
→ extract_structured_batch.py
→ validate_extracted.py
→ promote_structured_extractions.py
→ review_promoted_extractions.py
```

---

## Fluxo MVP normal

```bash
python3 tools/run_mvp_flow.py
```

Se houver pendências, gera:

```text
outputs/manual-review-pack.json
outputs/manual-review-pack.report.md
```

Depois de preencher o pacote:

```bash
python3 tools/continue_after_manual_review.py
```

---

## Fluxo com OCR preparado

Preparar documentos:

```bash
python3 tools/prepare_raw_for_ocr.py
```

Rodar fluxo preparado:

```bash
python3 tools/run_prepared_raw_flow.py
```

Esse fluxo usa:

```text
outputs/raw_prepared_for_ocr/
```

e gera:

```text
outputs/extracted_text_prepared/
outputs/structured_extractions_prepared/
outputs/promoted_extractions_prepared/
outputs/review-promoted-extractions-prepared.*
```

---

## Comparação OCR normal vs OCR preparado

```bash
python3 tools/compare_ocr_outputs.py
```

Saídas:

```text
outputs/compare-ocr-outputs.json
outputs/compare-ocr-outputs.report.md
```

---

## Seleção do melhor OCR

```bash
python3 tools/select_best_ocr_outputs.py
```

Compara:

```text
outputs/extracted_text/
outputs/extracted_text_prepared/
```

e gera:

```text
outputs/extracted_text_best/
outputs/select-best-ocr-outputs.json
outputs/select-best-ocr-outputs.report.md
```

Critério atual:

```text
seleciona o texto com mais caracteres
em caso de empate, prefere OCR normal
```

---

## Fluxo best OCR

```bash
python3 tools/run_best_ocr_flow.py
```

Fluxo:

```text
OCR normal
→ OCR preparado
→ comparação
→ seleção do melhor OCR
→ extração estruturada
→ promoção
→ revisão assistida
```

Saídas principais:

```text
outputs/extracted_text_best/
outputs/structured_extractions_best/
outputs/promoted_extractions_best/
outputs/review-promoted-extractions-best.json
outputs/review-promoted-extractions-best.report.md
```

---

## MVP best OCR

```bash
python3 tools/run_best_mvp_flow.py
```

Fluxo:

```text
best OCR
→ revisão assistida
→ pacote manual best
→ aprovação segura
→ JSON canônico best
→ exportação experimental best
```

Se houver pendências, gera:

```text
outputs/manual-review-pack-best.json
outputs/manual-review-pack-best.report.md
```

Depois de preencher:

```bash
python3 tools/continue_after_best_manual_review.py
```

Saídas finais:

```text
outputs/approved_best/
outputs/irpf-consolidado-best.json
outputs/irpf-consolidado-best.report.md
outputs/irpf-export-dec-experimental-best.txt
outputs/irpf-export-dec-experimental-best.report.md
```

---

## Revisão humana

Pacote normal:

```text
outputs/manual-review-pack.json
```

Pacote best:

```text
outputs/manual-review-pack-best.json
```

Itens aparecem assim:

```json
{
  "field": "cpf_declarante",
  "current_value": "11122233344",
  "reasons": [
    "CPF inválido"
  ],
  "suggested_value": null,
  "status": "pending"
}
```

Para corrigir:

```json
"suggested_value": "12345678909",
"status": "resolved"
```

Para CNPJ:

```json
"suggested_value": "11222333000181",
"status": "resolved"
```

Depois rode:

```bash
python3 tools/irpf_ocr.py continue
```

ou:

```bash
make continue
```

---

## Exportação experimental pré-DEC

Normal:

```bash
python3 tools/export_dec_experimental.py
```

Best:

```bash
python3 tools/export_dec_experimental.py   outputs/irpf-consolidado-best.json   outputs/irpf-export-dec-experimental-best.txt   outputs/irpf-export-dec-experimental-best.report.md
```

Importante:

```text
Esse arquivo NÃO é um .DEC oficial.
Não deve ser importado no PGD.
Serve apenas para estudo de mapeamento futuro.
```

---

## Saídas principais

### Normal

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
outputs/irpf-export-dec-experimental.txt
outputs/irpf-export-dec-experimental.report.md
```

### Best OCR

```text
outputs/irpf-consolidado-best.json
outputs/irpf-consolidado-best.report.md
outputs/irpf-export-dec-experimental-best.txt
outputs/irpf-export-dec-experimental-best.report.md
```

---

## Regras de segurança

O projeto deve bloquear avanço automático quando houver:

```text
CPF inválido
CNPJ inválido
CPF/CNPJ inválido
campo obrigatório ausente
campo com baixa confiança
documento desconhecido
documento que exige OCR/revisão manual
JSON canônico inválido
```

---

## Observações sobre OCR real

Documentos reais podem falhar por:

```text
imagem borrada
foto torta
documento cortado
baixa resolução
texto quebrado pelo OCR
campos sem rótulo
CPF/CNPJ ausente
classificação ambígua
```

O comportamento esperado nesses casos é gerar revisão humana, não avançar automaticamente.

---

## Desenvolvimento

Sempre que alterar o projeto:

```bash
python3 tests/run_tests.py
python3 tools/dev_check.py
python3 tools/check_repo_safety.py
```

Se passar:

```bash
git status
git add .
git commit -m "Mensagem objetiva"
git push
```

---

## Arquivos locais de teste

Pastas como estas são usadas apenas localmente:

```text
inputs/raw_test_*/
outputs/*_test_*
outputs/*-test-*
outputs/approved_test*
outputs/approved_best*
outputs/promoted_test*
outputs/promoted_extractions_best*
outputs/structured_extractions_test*
outputs/extracted_text_test*
outputs/extracted_text_best*
```

---

## GitHub

Repositório remoto usado no projeto:

```text
git@github.com:aksbarbosa/agentetributarioocr.git
```

---

## Próximas etapas

```text
1. Criar testes adicionais para fluxos best e setup.
2. Usar config/ocr_config.json dentro dos scripts de pré-processamento.
3. Criar modo interativo para preencher manual-review-pack.json.
4. Melhorar extração de dados de imóveis reais.
5. Criar fixtures reais anonimizadas.
6. Estudar layout real .DEC.
7. Evoluir exportador experimental para mapeamento por registros.
8. Criar exportador .DEC oficial apenas depois de mapear o layout corretamente.
```

---

## Limitações atuais

O projeto ainda não faz:

```text
geração oficial de .DEC
garantia de compatibilidade com PGD
interpretação jurídica/contábil
substituição de revisão humana
extração perfeita em OCR ruim
validação fiscal completa
```

---

## Aviso final

Este projeto é experimental e serve como apoio técnico à organização de documentos de IRPF.

Ele não substitui:

```text
conferência manual
contador
orientação tributária
validação no PGD oficial da Receita Federal
```
