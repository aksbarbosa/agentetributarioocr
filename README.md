# IRPF OCR DEC

Projeto experimental para construção de uma skill/agente para organizar dados de IRPF a partir de documentos, textos extraídos ou extrações estruturadas.

## Aviso importante

Este projeto não substitui contador, revisão humana, PGD oficial da Receita Federal ou responsabilidade do contribuinte.

## Estado atual

O projeto possui:

- classificador simples;
- simulador local individual;
- simulador local em lote;
- pré-triagem de documentos;
- pipeline para extrações simuladas;
- validação canônica;
- relatório humano;
- limpeza de outputs conhecidos;
- checagem de desenvolvimento integrada;
- resumo final da checagem de desenvolvimento;
- testes automatizados.

Ainda não possui OCR real, leitura direta de PDF/imagem, geração `.DEC` ou integração final com Agno.

## Fluxo correto

```text
documento
    ↓
OCR ou texto extraído
    ↓
classificação
    ↓
pré-triagem
    ↓
extração estruturada
    ↓
JSON canônico
    ↓
validação
    ↓
relatório humano
    ↓
revisão
    ↓
geração futura do .DEC
```

## Checagem de desenvolvimento

Arquivo:

```text
tools/dev_check.py
```

Comando:

```bash
python3 tools/dev_check.py
```

A checagem executa:

```text
1. Validar configuração
2. Limpar outputs
3. Rodar pré-triagem de documentos
4. Rodar projeto
5. Rodar testes
```

Ao final, imprime:

```text
Checagem concluída com sucesso.

Etapas executadas:
- Validar configuração
- Limpar outputs
- Rodar pré-triagem de documentos
- Rodar projeto
- Rodar testes
```

A pré-triagem usada no `dev_check.py` roda apenas o cenário positivo:

```bash
python3 tools/preflight_documents.py tests/fixtures/raw_text
```

O cenário bloqueado com documento desconhecido retorna exit code `1` de propósito e fica coberto pelos testes automatizados.

## Pré-triagem de documentos

Arquivo:

```text
tools/preflight_documents.py
```

Saídas:

```text
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

Status possíveis:

```text
ready
blocked
```

## Limpeza de outputs

Arquivo:

```text
tools/clean_outputs.py
```

Remove:

```text
outputs/irpf-consolidado.json
outputs/irpf-consolidado.report.md
outputs/agent-decision.json
outputs/agent-decisions.json
outputs/agent-decisions.report.md
outputs/preflight-documents.json
outputs/preflight-documents.report.md
```

## Comandos principais

```bash
python3 tools/run_project.py
python3 tests/run_tests.py
python3 tools/dev_check.py
python3 tools/clean_outputs.py
```

## Git e versionamento

```bash
git status
python3 tools/dev_check.py
git add .
git commit -m "Mensagem objetiva do que mudou"
git push
```
