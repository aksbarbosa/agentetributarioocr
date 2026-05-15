# Documentação Técnica — IRPF OCR DEC

## 1. Visão geral

O IRPF OCR DEC é um MVP local para transformar documentos fiscais em dados estruturados revisáveis, consolidar essas informações em um JSON canônico de IRPF e gerar uma exportação experimental pré-DEC.

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
Geração oficial .DEC: não implementada
```

---

## 3. Interface principal

Comandos principais:

```bash
python3 tools/ocr_strategy_status.py
python3 tools/run_ocr_strategy.py
python3 tools/continue_after_ocr_strategy_review.py
```

### `ocr_strategy_status.py`

Mostra a estratégia OCR configurada em `config/ocr_config.json`.

### `run_ocr_strategy.py`

Executa o fluxo definido em `config/ocr_config.json`.

### `continue_after_ocr_strategy_review.py`

Continua o fluxo depois da revisão manual conforme a estratégia configurada.

---

## 4. Configuração OCR

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
normal   → run_mvp_flow.py
prepared → run_prepared_raw_flow.py
best     → run_best_mvp_flow.py
```

Continuação pós-revisão:

```text
normal → continue_after_manual_review.py
best   → continue_after_best_manual_review.py
```

A estratégia `prepared` ainda não possui continuação canônica completa.

---

## 5. Fluxo geral normal

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

Comando:

```bash
python3 tools/run_mvp_flow.py
```

Continuação:

```bash
python3 tools/continue_after_manual_review.py
```

---

## 6. Fluxo OCR preparado

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

## 7. Fluxo best OCR

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

Continuação best:

```bash
python3 tools/continue_after_best_manual_review.py
```

---

## 8. Seleção de melhor OCR

Scripts:

```text
tools/compare_ocr_outputs.py
tools/select_best_ocr_outputs.py
```

Critério atual:

```text
longest_text
```

Em empate, a configuração atual prefere o OCR normal:

```json
"prefer_original_on_tie": true
```

---

## 9. Revisão humana

Pacotes:

```text
outputs/manual-review-pack.json
outputs/manual-review-pack-best.json
```

Campos pendentes devem ser preenchidos assim:

```json
"suggested_value": "valor_corrigido",
"status": "resolved"
```

Depois roda-se a continuação correspondente.

---

## 10. Validações

Configuração principal:

```bash
python3 tools/validate_config.py config/project_config.json
```

Configuração OCR:

```bash
python3 tools/validate_ocr_config.py
```

Testes:

```bash
python3 tests/run_tests.py
```

Checagem completa:

```bash
python3 tools/dev_check.py
```

O `dev_check.py` deve executar:

```text
validate_config.py
validate_ocr_config.py
tests/run_tests.py
```

---

## 11. Tipos suportados

```text
recibo_medico
plano_saude
informe_rendimentos_pj
bem_imovel
bem_veiculo
```

Documentos desconhecidos são bloqueados.

---

## 12. Melhorias implementadas

```text
- run_project.py aceita input_dir customizado.
- run_mvp_flow.py bloqueia canônico inválido.
- review_promoted_extractions.py valida CPF/CNPJ.
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
```

---

## 13. Saídas principais

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

## 14. Decisões técnicas

### Bloqueio conservador

O projeto deve parar diante de dados incertos, em vez de gerar canônico/exportação com dados ruins.

### Revisão humana obrigatória

Campos ausentes, baixa confiança ou CPF/CNPJ inválidos exigem revisão.

### Exportação DEC ainda experimental

A exportação atual não é oficial e não deve ser importada no PGD.

### OCR best é experimental

A seleção por maior texto é heurística e ainda não garante melhor qualidade semântica.

### Configuração centralizada

A estratégia OCR deve ser controlada por `config/ocr_config.json`.

---

## 15. Uso diário recomendado

Ver estratégia:

```bash
python3 tools/ocr_strategy_status.py
```

Executar fluxo:

```bash
python3 tools/run_ocr_strategy.py
```

Se parar para revisão, editar o pacote indicado e depois rodar:

```bash
python3 tools/continue_after_ocr_strategy_review.py
```

Checar projeto:

```bash
python3 tools/dev_check.py
```

---

## 16. Limitações atuais

```text
- Não gera .DEC oficial.
- Não garante compatibilidade com PGD.
- OCR ainda pode falhar com imagem ruim.
- Extração heurística depende dos padrões textuais.
- Melhor OCR por comprimento não garante melhor interpretação.
- Ainda falta modo interativo para revisão manual.
- Ainda falta estudo detalhado do layout .DEC real.
```

---

## 17. Próximas etapas técnicas

```text
1. Criar testes adicionais para fluxos best.
2. Usar config/ocr_config.json dentro dos scripts de pré-processamento.
3. Criar modo interativo para preencher manual-review-pack.
4. Melhorar extração de dados de imóveis reais.
5. Criar fixtures reais anonimizadas.
6. Estudar layout .DEC real.
7. Evoluir exportador experimental para registros mais próximos do formato oficial.
```

---

## 18. Estado esperado antes de commit

Antes de qualquer commit importante:

```bash
python3 tools/validate_ocr_config.py
python3 tests/run_tests.py
python3 tools/dev_check.py
```

Se passar:

```bash
git status
git add .
git commit -m "Mensagem objetiva"
git push
```
