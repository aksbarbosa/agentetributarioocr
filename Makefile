.PHONY: help setup status project-status run continue check test safety clean validate-config validate-ocr-config raw best prepared

PYTHON := python3

help:
	@echo "IRPF OCR DEC - comandos principais"
	@echo ""
	@echo "Setup e checagem:"
	@echo "  make setup              Configura projeto, instala hooks e roda checagens"
	@echo "  make check              Roda dev_check.py"
	@echo "  make test               Roda testes unitários"
	@echo "  make safety             Checa arquivos sensíveis rastreados pelo Git"
	@echo ""
	@echo "Interface principal:"
	@echo "  make status             Mostra estratégia OCR configurada"
	@echo "  make project-status     Mostra status dos outputs e próximo passo provável"
	@echo "  make run                Executa fluxo configurado em config/ocr_config.json"
	@echo "  make continue           Continua após revisão manual conforme estratégia OCR"
	@echo ""
	@echo "Fluxos específicos:"
	@echo "  make raw                Fluxo raw normal até revisão"
	@echo "  make prepared           Fluxo com OCR preparado até revisão"
	@echo "  make best               Fluxo best OCR até revisão"
	@echo ""
	@echo "Configuração:"
	@echo "  make validate-config     Valida config/project_config.json"
	@echo "  make validate-ocr-config Valida config/ocr_config.json"
	@echo ""
	@echo "Limpeza:"
	@echo "  make clean              Limpa outputs conforme clean_outputs.py"

setup:
	$(PYTHON) tools/irpf_ocr.py setup

status:
	$(PYTHON) tools/irpf_ocr.py status

project-status:
	$(PYTHON) tools/irpf_ocr.py project-status

run:
	$(PYTHON) tools/irpf_ocr.py run

continue:
	$(PYTHON) tools/irpf_ocr.py continue

check:
	$(PYTHON) tools/irpf_ocr.py check

test:
	$(PYTHON) tests/run_tests.py

safety:
	$(PYTHON) tools/check_repo_safety.py

validate-config:
	$(PYTHON) tools/validate_config.py config/project_config.json

validate-ocr-config:
	$(PYTHON) tools/validate_ocr_config.py

raw:
	$(PYTHON) tools/run_raw_flow.py

prepared:
	$(PYTHON) tools/run_prepared_raw_flow.py

best:
	$(PYTHON) tools/run_best_ocr_flow.py

clean:
	$(PYTHON) tools/clean_outputs.py
