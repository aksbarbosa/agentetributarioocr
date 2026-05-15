# Documentação Técnica — IRPF OCR DEC

## 1. Visão geral

O projeto IRPF OCR DEC é um MVP local para transformar documentos fiscais em dados estruturados revisáveis, consolidar essas informações em um JSON canônico de IRPF e gerar uma exportação experimental pré-DEC.

O projeto ainda não gera `.DEC` oficial compatível com o PGD da Receita Federal.

---

## 2. Estado atual

```text
Pipeline canônico: funcional
Pipeline raw-to-structured: funcional
OCR local com Tesseract: funcional
Fluxo de revisão humana: funcional
Aplicação de correções manuais: funcional
Exportação experimental pré-DEC: funcional
Estratégia OCR configurável: funcional
Fluxo best OCR: funcional/experimental
Interface unificada: funcional
Makefile: funcional
CI GitHub Actions: funcional/em validação
Geração oficial .DEC: não implementada
```

---

## 3. Interface operacional principal

A interface principal do projeto é:

```bash
python3 tools/irpf_ocr.py <comando>
```

Comandos disponíveis:

```bash
python3 tools/irpf_ocr.py setup
python3 tools/irpf_ocr.py status
python3 tools/irpf_ocr.py project-status
python3 tools/irpf_ocr.py run
python3 tools/irpf_ocr.py continue
python3 tools/irpf_ocr.py check
```

Significado:

```text
setup           configura o projeto, instala hooks e roda checagens
status          mostra a estratégia OCR configurada
project-status  mostra estado dos outputs e próximo passo provável
run             executa o fluxo definido em config/ocr_config.json
continue        continua depois da revisão manual conforme estratégia OCR
check           roda validações e testes
```

---

## 4. Atalhos via Makefile

O projeto possui `Makefile` com atalhos para os comandos mais usados:

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

Equivalências:

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

## 5. Configuração OCR

Arquivo:

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
normal   → tools/run_mvp_flow.py
prepared → tools/run_prepared_raw_flow.py
best     → tools/run_best_mvp_flow.py
```

Continuação pós-revisão:

```text
normal → tools/continue_after_manual_review.py
best   → tools/continue_after_best_manual_review.py
```

A estratégia `prepared` ainda não possui continuação canônica completa.

Validação:

```bash
python3 tools/validate_ocr_config.py
```

Status:

```bash
python3 tools/ocr_strategy_status.py
```

Execução da estratégia configurada:

```bash
python3 tools/run_ocr_strategy.py
```

Continuação conforme estratégia configurada:

```bash
python3 tools/continue_after_ocr_strategy_review.py
```

---

## 6. Fluxo geral normal

```text
inputs/raw/
→ extract_text.py
→ preflight_documents.py
→ extract_structured_batch.py
→ validate_extracted.py
→ promote_structured_extractions.py
→ review_promoted_extractions.py
→ generate_manual_review_pack.py
→ apply_manual_review_pack.py
→ approve_promoted_extractions.py
→ run_project.py
→ export_dec_experimental.py
```

Comando principal:

```bash
python3 tools/run_mvp_flow.py
```

Continuação após revisão:

```bash
python3 tools/continue_after_manual_review.py
```

---

## 7. Fluxo OCR preparado

```text
inputs/raw/
→ prepare_raw_for_ocr.py
→ outputs/raw_prepared_for_ocr/
→ extract_text.py
→ outputs/extracted_text_prepared/
→ extract_structured_batch.py
→ promoted/review prepared
```

Comando:

```bash
python3 tools/run_prepared_raw_flow.py
```

Esse fluxo é útil para testar se pré-processamento melhora o OCR.

---

## 8. Fluxo best OCR

```text
OCR normal
→ OCR preparado
→ compare_ocr_outputs.py
→ select_best_ocr_outputs.py
→ outputs/extracted_text_best/
→ extract_structured_batch.py
→ promote
→ review
```

Comando:

```bash
python3 tools/run_best_ocr_flow.py
```

MVP completo best:

```bash
python3 tools/run_best_mvp_flow.py
```

Continuação após revisão best:

```bash
python3 tools/continue_after_best_manual_review.py
```

---

## 9. Seleção de melhor OCR

Scripts:

```text
tools/compare_ocr_outputs.py
tools/select_best_ocr_outputs.py
```

Critério atual:

```text
longest_text
```

Isto é, o texto com maior número de caracteres é selecionado.

Em empate, a configuração atual prefere o OCR normal:

```json
"prefer_original_on_tie": true
```

Observação técnica: esse critério é heurístico. Texto mais longo não garante necessariamente texto semanticamente melhor, mas é uma boa aproximação inicial para comparar OCR normal e OCR pré-processado.

---

## 10. Revisão humana

A revisão humana é central para segurança.

Pacotes principais:

```text
outputs/manual-review-pack.json
outputs/manual-review-pack-best.json
```

Campos pendentes devem ser preenchidos assim:

```json
"suggested_value": "valor_corrigido",
"status": "resolved"
```

Depois roda-se a continuação correspondente:

```bash
python3 tools/irpf_ocr.py continue
```

ou:

```bash
make continue
```

---

## 11. Validações

### Configuração principal

```bash
python3 tools/validate_config.py config/project_config.json
```

### Configuração OCR

```bash
python3 tools/validate_ocr_config.py
```

### Segurança do repositório

```bash
python3 tools/check_repo_safety.py
```

### Testes

```bash
python3 tests/run_tests.py
```

### Checagem completa

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

## 12. CI / GitHub Actions

O CI está definido em:

```text
.github/workflows/ci.yml
```

Etapas executadas:

```text
checkout
setup Python
instalação de dependências OCR
instalação de requirements.txt
validação da configuração principal
validação da configuração OCR
checagem de segurança do repositório
testes unitários
dev_check.py
```

A falha do CI deve bloquear a evolução até ser corrigida.

---

## 13. Segurança do repositório

O projeto possui proteção para evitar commit acidental de documentos reais e artefatos de OCR.

Arquivos e pastas bloqueados:

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

Checagem:

```bash
python3 tools/check_repo_safety.py
```

Instalação de hook local:

```bash
python3 tools/install_git_hooks.py
```

Hook versionado:

```text
scripts/git-hooks/pre-commit
```

Destino local:

```text
.git/hooks/pre-commit
```

---

## 14. Document types suportados

```text
recibo_medico
plano_saude
informe_rendimentos_pj
bem_imovel
bem_veiculo
```

Documentos desconhecidos são bloqueados.

---

## 15. Melhorias recentes implementadas

```text
- run_project.py passou a aceitar input_dir customizado.
- run_mvp_flow.py passou a bloquear canônico inválido.
- review_promoted_extractions.py passou a validar CPF/CNPJ.
- generate_manual_review_pack.py cria pacote de revisão humana.
- apply_manual_review_pack.py aplica correções manuais.
- continue_after_manual_review.py continua fluxo após revisão.
- export_dec_experimental.py gera exportação pré-DEC experimental.
- preprocess_raw_images.py e prepare_raw_for_ocr.py ajudam em OCR ruim.
- compare_ocr_outputs.py compara OCR normal vs preparado.
- select_best_ocr_outputs.py escolhe melhor OCR.
- run_best_ocr_flow.py roda pipeline best OCR até revisão.
- run_best_mvp_flow.py tenta fechar MVP usando best OCR.
- continue_after_best_manual_review.py continua o fluxo best após revisão.
- config/ocr_config.json centraliza a estratégia OCR.
- run_ocr_strategy.py executa a estratégia configurada.
- continue_after_ocr_strategy_review.py continua conforme a estratégia configurada.
- irpf_ocr.py fornece interface unificada.
- Makefile fornece atalhos operacionais.
- check_repo_safety.py protege contra arquivos sensíveis rastreados.
- install_git_hooks.py instala hook local de segurança.
- GitHub Actions executa validações e testes no push/pull request.
```

---

## 16. Saídas principais

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

### Diagnóstico OCR

```text
outputs/compare-ocr-outputs.json
outputs/compare-ocr-outputs.report.md
outputs/select-best-ocr-outputs.json
outputs/select-best-ocr-outputs.report.md
```

---

## 17. Decisões técnicas

### Decisão 1 — Bloqueio conservador

O projeto deve parar diante de dados incertos, em vez de gerar canônico/exportação com dados ruins.

### Decisão 2 — Revisão humana obrigatória

Campos ausentes, baixa confiança ou CPF/CNPJ inválidos exigem revisão.

### Decisão 3 — Exportação DEC ainda experimental

A exportação atual não é oficial e não deve ser importada no PGD.

### Decisão 4 — OCR best é experimental

A seleção por maior texto é heurística, útil para comparação, mas ainda não garante melhor qualidade semântica.

### Decisão 5 — Configuração centralizada

A estratégia OCR deve ser controlada por `config/ocr_config.json`.

### Decisão 6 — Segurança por padrão

Documentos reais, imagens, PDFs, outputs e `.DEC` não devem ser rastreados pelo Git.

---

## 18. Comandos recomendados no uso diário

Ver estratégia:

```bash
python3 tools/irpf_ocr.py status
```

Executar fluxo:

```bash
python3 tools/irpf_ocr.py run
```

Se parar para revisão, editar o pacote indicado e depois rodar:

```bash
python3 tools/irpf_ocr.py continue
```

Checar projeto:

```bash
python3 tools/irpf_ocr.py check
```

Atalhos equivalentes:

```bash
make status
make run
make continue
make check
```

---

## 19. Limitações atuais

```text
- Não gera .DEC oficial.
- Não garante compatibilidade com PGD.
- OCR ainda pode falhar com imagem ruim.
- Extração heurística ainda depende dos padrões textuais.
- Melhor OCR por comprimento não garante melhor interpretação.
- Ainda falta modo interativo para revisão manual.
- Ainda falta estudo detalhado do layout .DEC real.
```

---

## 20. Próximas etapas técnicas

```text
1. Atualizar README e DOCUMENTACAO continuamente.
2. Criar testes adicionais para fluxos best.
3. Usar config/ocr_config.json dentro dos scripts de pré-processamento.
4. Criar modo interativo para preencher manual-review-pack.
5. Melhorar extração de dados de imóveis reais.
6. Criar fixtures reais anonimizadas.
7. Estudar layout .DEC real.
8. Evoluir exportador experimental para registros mais próximos do formato oficial.
```

---

## 21. Estado esperado antes de commit

Antes de qualquer commit importante:

```bash
python3 tools/validate_ocr_config.py
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
