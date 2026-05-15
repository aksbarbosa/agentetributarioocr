# Changelog — IRPF OCR DEC

Todas as mudanças relevantes deste projeto serão documentadas aqui.

O formato é inspirado em Keep a Changelog, mas adaptado ao estado experimental do projeto.

---

## [0.1.0] - MVP seguro local

### Adicionado

- Pipeline canônico para consolidar extrações em `outputs/irpf-consolidado.json`.
- Relatório humano em Markdown para revisão dos dados consolidados.
- Suporte inicial aos tipos documentais:
  - `recibo_medico`
  - `plano_saude`
  - `informe_rendimentos_pj`
  - `bem_imovel`
  - `bem_veiculo`
- Extração de texto de arquivos `.txt` e PDFs pesquisáveis.
- Marcação de arquivos que exigem OCR real.
- Classificador documental baseado em palavras-chave.
- Pré-triagem de documentos extraídos.
- Extração estruturada heurística a partir de texto.
- Validação de extrações estruturadas.
- Promoção segura de extrações para entrada canônica.
- Revisão assistida de extrações promovidas.
- Validação de CPF, CNPJ e CPF/CNPJ em campos sensíveis.
- Geração de pacote de revisão manual:
  - `outputs/manual-review-pack.json`
  - `outputs/manual-review-pack.report.md`
- Aplicação de correções humanas via pacote manual.
- Continuação do fluxo após revisão manual.
- Aprovação segura de extrações corrigidas.
- Exportação experimental pré-DEC.
- Fluxo MVP normal:
  - `tools/run_mvp_flow.py`
  - `tools/continue_after_manual_review.py`
- Pré-processamento de imagens para OCR.
- Preparação de documentos brutos para OCR.
- Fluxo com OCR preparado.
- Comparação entre OCR normal e OCR preparado.
- Seleção heurística do melhor OCR por maior quantidade de texto.
- Fluxo best OCR:
  - `tools/run_best_ocr_flow.py`
  - `tools/run_best_mvp_flow.py`
  - `tools/continue_after_best_manual_review.py`
- Configuração centralizada de OCR em:
  - `config/ocr_config.json`
- Validador da configuração OCR:
  - `tools/validate_ocr_config.py`
- Executor de estratégia OCR:
  - `tools/run_ocr_strategy.py`
- Continuação pós-revisão baseada na estratégia OCR:
  - `tools/continue_after_ocr_strategy_review.py`
- Interface unificada:
  - `tools/irpf_ocr.py`
- Comando de setup:
  - `tools/setup_project.py`
- Makefile com atalhos operacionais.
- Checagem de segurança contra arquivos sensíveis rastreados pelo Git:
  - `tools/check_repo_safety.py`
- Hook local de pré-commit para segurança do repositório.
- Instalador de hooks:
  - `tools/install_git_hooks.py`
- Workflow de CI com GitHub Actions:
  - `.github/workflows/ci.yml`
- Documentação atualizada:
  - `README.md`
  - `DOCUMENTACAO.md`
- Testes unitários para os principais módulos do projeto.
- `dev_check.py` para validação de desenvolvimento.

### Alterado

- `run_project.py` passou a aceitar pasta de entrada customizada.
- O fluxo canônico passou a bloquear avanço quando o JSON consolidado é inválido.
- A revisão assistida passou a detectar identificadores inválidos.
- Os testes do fluxo raw foram ajustados para não depender de arquivos locais em `inputs/raw/`.
- O projeto passou a tratar documentos reais e outputs como artefatos locais não versionáveis.

### Segurança

- `inputs/raw/`, `inputs/raw_test_*/`, `inputs/raw_ignored/` e `outputs/` foram protegidos contra commit.
- Imagens, PDFs, arquivos `.DEC` e artefatos fiscais locais foram protegidos pelo `.gitignore`.
- `check_repo_safety.py` bloqueia arquivos sensíveis já rastreados pelo Git.
- Hook `pre-commit` local executa a checagem de segurança antes de commits.

### Limitações conhecidas

- O projeto ainda não gera `.DEC` oficial.
- A exportação pré-DEC é experimental.
- OCR pode falhar com imagens ruins, cortadas ou muito borradas.
- A seleção best OCR usa heurística de maior texto, que não garante melhor qualidade semântica.
- Ainda não há modo interativo para preencher pacote de revisão manual.
- Ainda falta estudo detalhado do layout real `.DEC`.

---

## [0.0.1] - Estrutura inicial

### Adicionado

- Estrutura inicial do projeto.
- Primeiros scripts de normalização, validação e simulação.
- Primeiros testes unitários.
