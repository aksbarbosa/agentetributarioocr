# IRPF OCR DEC

Projeto experimental para construção de uma skill/agente capaz de auxiliar na montagem inicial da Declaração de Imposto de Renda Pessoa Física a partir de documentos digitalizados, textos extraídos ou extrações estruturadas.

A ideia central é transformar documentos fiscais em um JSON canônico revisável e, futuramente, gerar um arquivo `.DEC` experimental importável no PGD oficial da Receita Federal.

---

## Aviso importante

Este projeto não substitui:

- contador;
- revisão humana;
- PGD oficial da Receita Federal;
- responsabilidade do contribuinte.

O objetivo é funcionar como um pré-processador inteligente:

1. organiza documentos;
2. classifica documentos;
3. simula decisões iniciais de agente;
4. normaliza dados;
5. valida inconsistências;
6. gera um relatório humano;
7. futuramente gera um `.DEC` experimental.

A responsabilidade final pela declaração continua sendo do contribuinte.

O fluxo correto é:

```text
documento
    ↓
OCR ou texto extraído
    ↓
classificação
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

---

## Estado atual do projeto

Nesta fase, o projeto ainda **não faz OCR real** e ainda **não gera `.DEC`**.

Atualmente ele possui quatro blocos funcionais:

1. **Classificador simples de documentos** a partir de texto bruto simulado;
2. **Simulador local de agente individual**, que classifica um texto e sugere o próximo passo;
3. **Simulador local de agente em lote**, que processa uma pasta de textos e gera decisões consolidadas;
4. **Pipeline principal**, que processa extrações simuladas em JSON e gera JSON canônico consolidado + relatório humano.

O classificador e os simuladores ainda não leem PDF ou imagem diretamente. Eles recebem texto previamente extraído ou fixtures simuladas.

---

## Fluxo atual do classificador

```text
tests/fixtures/raw_text/
    ↓
tools/classify_document.py
    ↓
document_type provável
```

---

## Fluxo atual do simulador local de agente individual

```text
tests/fixtures/raw_text/
    ↓
tools/agent_simulator.py
    ↓
classificação
    ↓
decisão
    ↓
schema recomendado
    ↓
próximo passo
```

---

## Fluxo atual do simulador local de agente em lote

```text
tests/fixtures/raw_text/
    ↓
tools/agent_batch_simulator.py
    ↓
classificação de cada documento
    ↓
decisão individual por documento
    ↓
outputs/agent-decisions.json
    ↓
outputs/agent-decisions.report.md
```

---

## Fluxo atual do pipeline principal

```text
inputs/extracted/
    ↓
tools/run_project.py
    ↓
validação da configuração
    ↓
validação das extrações
    ↓
normalização
    ↓
JSON canônico consolidado
    ↓
validação canônica
    ↓
relatório humano
```

---

## Documentos suportados atualmente

| Documento | `document_type` | Destino |
|---|---|---|
| Informe de rendimentos PJ | `informe_rendimentos_pj` | `rendimentos.tributaveis_pj[]` |
| Recibo médico | `recibo_medico` | `pagamentos[]` |
| Plano de saúde | `plano_saude` | `pagamentos[]` |
| Bem imóvel | `bem_imovel` | `bens[]` |
| Bem veículo | `bem_veiculo` | `bens[]` |

---

## Estrutura principal

```text
irpf_ocr_dec/
├── README.md
├── CHANGELOG.md
├── config/
│   └── project_config.json
├── inputs/
│   ├── raw/
│   │   └── .gitkeep
│   └── extracted/
├── outputs/
├── skill/
│   ├── SKILL.md
│   ├── instructions.md
│   ├── references/
│   └── schemas/
├── tests/
│   ├── fixtures/
│   │   ├── raw_text/
│   │   └── raw_text_with_unknown/
│   ├── run_tests.py
│   └── unit/
└── tools/
    ├── agent_batch_simulator.py
    ├── agent_simulator.py
    ├── build_canonical_json.py
    ├── classify_document.py
    ├── clean_outputs.py
    ├── dev_check.py
    ├── normalize.py
    ├── pipeline_batch.py
    ├── pipeline_from_extracted.py
    ├── report.py
    ├── run_project.py
    ├── validate.py
    ├── validate_config.py
    └── validate_extracted.py
```

---

## Pastas principais

### `inputs/raw/`

Pasta reservada para documentos originais no futuro.

Atualmente ainda não usamos OCR real, então essa pasta fica vazia, exceto pelo arquivo `.gitkeep`.

### `inputs/extracted/`

Pasta com arquivos JSON de extração.

Esses arquivos simulam a saída futura do OCR + extração estruturada.

Exemplos atuais:

```text
informe_pj_exemplo.json
recibo_medico_exemplo.json
plano_saude_exemplo.json
bem_imovel_exemplo.json
bem_veiculo_exemplo.json
```

### `tests/fixtures/raw_text/`

Pasta com textos brutos simulados, usados para testar o classificador simples, o simulador individual e o simulador em lote.

Exemplos atuais:

```text
crlv_veiculo_exemplo.txt
informe_pj_exemplo.txt
iptu_imovel_exemplo.txt
plano_saude_exemplo.txt
recibo_medico_exemplo.txt
```

Essa pasta representa o cenário em que todos os documentos são conhecidos e devem ser classificados corretamente.

### `tests/fixtures/raw_text_with_unknown/`

Pasta com os mesmos textos brutos suportados, mais um documento genérico desconhecido.

Ela é usada para testar o comportamento do simulador em lote quando algum arquivo exige revisão manual.

Exemplo:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown
```

Resultado esperado:

```text
Arquivos analisados: 6
Documentos aptos a continuar: 5
Documentos que exigem revisão manual: 1
```

### `outputs/`

Pasta onde ficam os resultados gerados.

Arquivos principais:

```text
irpf-consolidado.json
irpf-consolidado.report.md
agent-decision.json
agent-decisions.json
agent-decisions.report.md
```

Esses arquivos são gerados automaticamente e normalmente não devem ser versionados no Git.

---

## Arquivo de configuração

O projeto usa:

```text
config/project_config.json
```

Exemplo atual:

```json
{
  "project_name": "IRPF OCR DEC",
  "schema_version": "irpf-2026-v1",
  "exercicio": 2026,
  "ano_calendario": 2025,
  "tipo_declaracao": "AJUSTE_ANUAL",
  "modelo": "AUTO",
  "input_raw_dir": "inputs/raw",
  "input_extracted_dir": "inputs/extracted",
  "output_dir": "outputs",
  "output_json": "outputs/irpf-consolidado.json",
  "output_report": "outputs/irpf-consolidado.report.md",
  "fail_on_invalid_extraction": false,
  "fail_on_canonical_error": true,
  "enable_duplicate_detection": true,
  "enable_human_review_report": true
}
```

Validar configuração:

```bash
python3 tools/validate_config.py config/project_config.json
```

---

## Como rodar o projeto

Na raiz do projeto:

```bash
cd ~/Documents/irpf_ocr_dec
python3 tools/run_project.py
```

---

## Checagem de desenvolvimento

```bash
python3 tools/dev_check.py
```

Esse comando executa:

```text
1. validate_config.py
2. clean_outputs.py
3. run_project.py
4. tests/run_tests.py
```

Use esse comando sempre que alterar alguma parte importante do projeto.

---

## Comandos úteis

Rodar o projeto:

```bash
python3 tools/run_project.py
```

Rodar testes:

```bash
python3 tests/run_tests.py
```

Rodar checagem completa:

```bash
python3 tools/dev_check.py
```

Classificar texto bruto:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Classificar texto bruto com JSON:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Simular decisão local do agente individual:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Simular decisão local individual com JSON:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Salvar decisão local individual em JSON:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

Simular decisões locais em lote:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text
```

Simular decisões locais em lote com JSON no terminal:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text --json
```

Simular decisões em lote com caminhos customizados:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md
```

Simular decisões em lote com caminhos customizados e JSON no terminal:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md --json
```

Simular lote com documento desconhecido:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text_with_unknown
```

---

## Classificador simples de documentos

Arquivo principal:

```text
tools/classify_document.py
```

Ele recebe texto bruto e retorna:

- `document_type`;
- rótulo humano;
- confiança;
- pontuação por tipo de documento;
- palavras-chave encontradas.

Tipos reconhecidos:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
desconhecido
```

---

## Simulador local de agente individual

Arquivo principal:

```text
tools/agent_simulator.py
```

Ele recebe um arquivo de texto bruto, chama o classificador simples e retorna uma decisão estruturada.

A decisão contém:

```text
input_path
classification
decision
```

A seção `decision` informa:

```text
document_type
confidence
should_continue
schema_path
next_step
```

---

## Simulador local de agente em lote

Arquivo principal:

```text
tools/agent_batch_simulator.py
```

Ele recebe uma pasta com arquivos `.txt`, executa o simulador local para cada texto e gera:

```text
outputs/agent-decisions.json
outputs/agent-decisions.report.md
```

Também é possível imprimir o JSON consolidado no terminal:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text --json
```

Também é possível usar caminhos customizados e imprimir JSON no terminal:

```bash
python3 tools/agent_batch_simulator.py tests/fixtures/raw_text outputs/agent-decisions.json outputs/agent-decisions.report.md --json
```

O simulador em lote produz:

- decisões individuais;
- resumo por tipo de documento;
- resumo por confiança;
- contagem de documentos que podem continuar;
- contagem de documentos que exigem revisão manual.

Quando usado com a fixture `tests/fixtures/raw_text_with_unknown/`, o relatório deve destacar o documento desconhecido na seção:

```markdown
## Documentos que exigem revisão manual
```

---

## JSON canônico

Formato resumido:

```json
{
  "$schema": "irpf-2026-v1",
  "exercicio": 2026,
  "ano_calendario": 2025,
  "tipo_declaracao": "AJUSTE_ANUAL",
  "modelo": "AUTO",
  "declarante": {},
  "rendimentos": {
    "tributaveis_pj": []
  },
  "pagamentos": [],
  "bens": [],
  "dividas": [],
  "avisos": [],
  "requires_review": []
}
```

---

## Validações atuais

O projeto já valida:

- configuração do projeto;
- CPF do declarante;
- data de nascimento;
- CNPJ da fonte pagadora;
- CPF ou CNPJ de prestadores;
- campos obrigatórios das extrações;
- valores negativos;
- pagamento com valor zero;
- códigos de pagamento;
- duplicidade simples de pagamentos;
- conflitos em dados do declarante;
- bens imóveis básicos;
- bens veículos básicos;
- CEP;
- UF;
- data de aquisição de bem;
- RENAVAM;
- placa;
- marca, modelo e ano de fabricação;
- estrutura mínima do JSON canônico.

---

## Testes automatizados

Atualmente os testes cobrem:

```text
normalize.py
validate.py
validate_config.py
validate_extracted.py
build_canonical_json.py
pipeline_batch.py
run_project.py
report.py
clean_outputs.py
classify_document.py
agent_simulator.py
agent_batch_simulator.py
```

---

## Ferramentas principais

### `tools/agent_batch_simulator.py`

Protótipo local de comportamento de agente em lote.

### `tools/agent_simulator.py`

Protótipo local de comportamento de agente individual.

### `tools/classify_document.py`

Classificador simples por palavras-chave.

### `tools/run_project.py`

Comando principal do projeto.

### `tools/dev_check.py`

Roda validação de configuração, limpeza, pipeline principal e testes.

---

## Git e versionamento

Fluxo recomendado:

```bash
git status
python3 tools/dev_check.py
git add .
git commit -m "Mensagem objetiva do que mudou"
git push
```

---

## Próximas etapas planejadas

1. Melhorar o simulador local de agente em lote.
2. Melhorar o simulador local de agente individual.
3. Melhorar o classificador simples de documentos.
4. Preparar OCR real.
5. Criar camada de leitura de PDF/imagem.
6. Criar builder `.DEC` experimental.
7. Criar parser reverso `.DEC`.
8. Expandir suporte a dependentes, investimentos e outros rendimentos.
9. Criar testes adicionais para novos documentos.
10. Integrar a skill ao agente Agno.

---

## Limitações atuais

O projeto ainda não possui:

- OCR real;
- leitura de PDF/imagem;
- classificação automática robusta de documentos reais;
- geração de `.DEC`;
- transmissão da declaração;
- parser reverso `.DEC`;
- suporte a dependentes;
- suporte a investimentos;
- suporte a rendimentos isentos/exclusivos;
- suporte a atividade rural;
- cálculo completo de imposto.

---

## Filosofia do projeto

```text
OCR é probabilístico.
Classificação inicial pode ser probabilística ou heurística.
Validação e geração de saída devem ser determinísticas.
```

O fluxo correto é:

```text
documento
    ↓
OCR ou texto extraído
    ↓
classificação
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
