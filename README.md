# IRPF OCR DEC

Projeto experimental para construção de uma skill/agente capaz de auxiliar na montagem inicial da Declaração de Imposto de Renda Pessoa Física a partir de documentos digitalizados, textos extraídos ou extrações estruturadas.

A ideia central do projeto é transformar documentos fiscais em um JSON canônico revisável e, futuramente, gerar um arquivo `.DEC` experimental importável no PGD oficial da Receita Federal.

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
3. extrai informações;
4. normaliza dados;
5. valida inconsistências;
6. gera um relatório humano;
7. futuramente gera um `.DEC` experimental.

A responsabilidade final pela declaração continua sendo do contribuinte.

---

## Estado atual do projeto

Nesta fase, o projeto ainda **não faz OCR real** e ainda **não gera `.DEC`**.

Atualmente ele possui três blocos funcionais:

1. **Classificador simples de documentos** a partir de texto bruto simulado;
2. **Simulador local de agente**, que classifica o texto e sugere o próximo passo;
3. **Pipeline principal**, que processa extrações simuladas em JSON e gera JSON canônico consolidado + relatório humano.

O classificador e o simulador ainda não leem PDF ou imagem diretamente. Eles recebem texto previamente extraído ou fixtures simuladas.

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

## Fluxo atual do simulador local de agente

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

### Informe de rendimentos PJ

```json
{
  "document_type": "informe_rendimentos_pj"
}
```

Gera dados em `rendimentos.tributaveis_pj[]`.

### Recibo médico

```json
{
  "document_type": "recibo_medico"
}
```

Gera dados em `pagamentos[]` com código `10`.

### Plano de saúde

```json
{
  "document_type": "plano_saude"
}
```

Gera dados em `pagamentos[]` com código `26`.

### Bem imóvel

```json
{
  "document_type": "bem_imovel"
}
```

Gera dados em `bens[]`.

Exemplo atual:

```text
tipo_bem = IMOVEL
grupo_bem = 01
codigo_bem = 11
```

### Bem veículo

```json
{
  "document_type": "bem_veiculo"
}
```

Gera dados em `bens[]`.

Exemplo atual:

```text
tipo_bem = VEICULO
grupo_bem = 02
codigo_bem = 01
```

---

## Estrutura do projeto

```text
irpf_ocr_dec/
├── CHANGELOG.md
├── README.md
├── config/
│   └── project_config.json
├── inputs/
│   ├── raw/
│   │   └── .gitkeep
│   └── extracted/
│       ├── bem_imovel_exemplo.json
│       ├── bem_veiculo_exemplo.json
│       ├── informe_pj_exemplo.json
│       ├── plano_saude_exemplo.json
│       └── recibo_medico_exemplo.json
├── outputs/
│   ├── irpf-consolidado.json
│   └── irpf-consolidado.report.md
├── skill/
│   ├── SKILL.md
│   ├── instructions.md
│   ├── references/
│   │   ├── codigos_bens.md
│   │   ├── codigos_pagamentos.md
│   │   ├── json_canonico.md
│   │   ├── pipeline.md
│   │   └── tipos_documentos.md
│   └── schemas/
│       ├── canonical_irpf_2026.json
│       ├── extracted_bem_imovel.json
│       ├── extracted_bem_veiculo.json
│       ├── extracted_informe_pj.json
│       ├── extracted_plano_saude.json
│       ├── extracted_recibo_medico.json
│       └── project_config.json
├── tests/
│   ├── fixtures/
│   │   └── raw_text/
│   │       ├── crlv_veiculo_exemplo.txt
│   │       ├── informe_pj_exemplo.txt
│   │       ├── iptu_imovel_exemplo.txt
│   │       ├── plano_saude_exemplo.txt
│   │       └── recibo_medico_exemplo.txt
│   ├── run_tests.py
│   └── unit/
│       ├── test_agent_simulator.py
│       ├── test_build_canonical_json.py
│       ├── test_classify_document.py
│       ├── test_clean_outputs.py
│       ├── test_normalize.py
│       ├── test_pipeline_batch.py
│       ├── test_report.py
│       ├── test_run_project.py
│       ├── test_validate.py
│       ├── test_validate_config.py
│       └── test_validate_extracted.py
└── tools/
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

Pasta reservada para documentos originais no futuro. Atualmente ainda não usamos OCR real, então essa pasta fica vazia, exceto pelo `.gitkeep`.

### `inputs/extracted/`

Pasta com arquivos JSON de extração. Esses arquivos simulam a saída futura do OCR + extração estruturada.

### `tests/fixtures/raw_text/`

Pasta com textos brutos simulados, usados para testar o classificador simples de documentos e o simulador local de agente.

### `outputs/`

Pasta onde ficam os resultados gerados. Arquivos principais:

```text
irpf-consolidado.json
irpf-consolidado.report.md
```

Esses arquivos são gerados automaticamente pelo pipeline e normalmente não devem ser versionados no Git.

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

O arquivo de configuração é validado por:

```text
tools/validate_config.py
```

Para validar manualmente:

```bash
python3 tools/validate_config.py config/project_config.json
```

O comando principal também valida automaticamente o arquivo de configuração antes de executar o pipeline.

O schema formal da configuração está em:

```text
skill/schemas/project_config.json
```

---

## Como rodar o projeto

Na raiz do projeto:

```bash
cd ~/Documents/irpf_ocr_dec
```

Execute:

```bash
python3 tools/run_project.py
```

Saída esperada:

```text
Validação da configuração:
Configuração válida.

Pipeline em lote finalizado.
Pasta de entrada: inputs/extracted
JSON consolidado: outputs/irpf-consolidado.json
Relatório consolidado: outputs/irpf-consolidado.report.md
Arquivos processados: 5
Arquivos ignorados: 0
Extrações inválidas fatais: 0

Validação do JSON consolidado: válido.
```

---

## Ver os resultados

Para ver o JSON consolidado:

```bash
cat outputs/irpf-consolidado.json
```

Para abrir o relatório:

```bash
open outputs/irpf-consolidado.report.md
```

---

## Checagem de desenvolvimento

Na raiz do projeto, rode:

```bash
python3 tools/dev_check.py
```

Esse comando executa:

```text
1. python3 tools/validate_config.py config/project_config.json
2. python3 tools/clean_outputs.py
3. python3 tools/run_project.py
4. python3 tests/run_tests.py
```

A saída esperada termina com:

```text
Checagem concluída com sucesso.
```

---

## Comandos úteis

Rodar o projeto:

```bash
python3 tools/run_project.py
```

Validar configuração:

```bash
python3 tools/validate_config.py config/project_config.json
```

Rodar testes:

```bash
python3 tests/run_tests.py
```

Rodar checagem completa de desenvolvimento:

```bash
python3 tools/dev_check.py
```

Limpar outputs:

```bash
python3 tools/clean_outputs.py
```

Validar uma extração individual:

```bash
python3 tools/validate_extracted.py inputs/extracted/informe_pj_exemplo.json
```

Rodar pipeline para uma extração individual:

```bash
python3 tools/pipeline_from_extracted.py inputs/extracted/recibo_medico_exemplo.json
```

Rodar pipeline em lote diretamente pela pasta:

```bash
python3 tools/pipeline_batch.py inputs/extracted
```

Rodar pipeline em lote usando configuração:

```bash
python3 tools/pipeline_batch.py --config config/project_config.json
```

Classificar texto bruto simulado:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Classificar texto bruto simulado com saída JSON:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Simular decisão local do agente:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Simular decisão local do agente com saída JSON:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Salvar decisão local do agente em JSON:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

Conferir a decisão salva:

```bash
cat outputs/agent-decision.json
```

---

## Classificador simples de documentos

O projeto possui um classificador inicial baseado em palavras-chave.

Arquivo principal:

```text
tools/classify_document.py
```

Ele recebe um arquivo de texto e tenta identificar o `document_type`.

Tipos reconhecidos atualmente:

```text
informe_rendimentos_pj
recibo_medico
plano_saude
bem_imovel
bem_veiculo
desconhecido
```

Também existe saída JSON:

```bash
python3 tools/classify_document.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Fixtures atuais:

```text
tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
tests/fixtures/raw_text/informe_pj_exemplo.txt
tests/fixtures/raw_text/iptu_imovel_exemplo.txt
tests/fixtures/raw_text/plano_saude_exemplo.txt
tests/fixtures/raw_text/recibo_medico_exemplo.txt
```

Teste relacionado:

```text
tests/unit/test_classify_document.py
```

---

## Simulador local de agente

O projeto possui um primeiro protótipo local de comportamento de agente:

```text
tools/agent_simulator.py
```

Ele recebe um arquivo de texto bruto, chama o classificador simples e retorna uma decisão estruturada.

Fluxo atual:

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

Exemplo:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt
```

Também há saída JSON no terminal:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --json
```

Também é possível salvar a decisão estruturada em arquivo:

```bash
python3 tools/agent_simulator.py tests/fixtures/raw_text/crlv_veiculo_exemplo.txt --save-json outputs/agent-decision.json
```

Esse JSON contém:

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

Esse simulador ainda não é o agente Agno final. Ele serve para testar localmente a lógica de decisão antes da integração com Agno.

Teste relacionado:

```text
tests/unit/test_agent_simulator.py
```

---

## JSON canônico

O JSON canônico é o formato interno da declaração.

Exemplo simplificado:

```json
{
  "$schema": "irpf-2026-v1",
  "exercicio": 2026,
  "ano_calendario": 2025,
  "tipo_declaracao": "AJUSTE_ANUAL",
  "modelo": "AUTO",
  "declarante": {
    "cpf": "12345678909",
    "nome": "JOSE DA SILVA",
    "data_nascimento": "01011980"
  },
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

## Exemplo de bem imóvel no JSON canônico

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

## Exemplo de bem veículo no JSON canônico

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

## Regras importantes

### Valores monetários

Todos os valores monetários são armazenados em centavos inteiros.

```text
R$ 85.000,00   → 8500000
R$ 500,00      → 50000
R$ 3.600,00    → 360000
R$ 80.000,00   → 8000000
R$ 250.000,00  → 25000000
```

### CPF e CNPJ

CPF e CNPJ são armazenados apenas com dígitos.

```text
123.456.789-09     → 12345678909
11.222.333/0001-81 → 11222333000181
```

### Datas

Datas são armazenadas no formato `DDMMAAAA`.

```text
15/03/2025 → 15032025
10/05/2020 → 10052020
20/08/2020 → 20082020
```

### Nomes

Nomes são normalizados em maiúsculas e sem acentos nesta fase.

```text
José da Silva → JOSE DA SILVA
São Paulo     → SAO PAULO
Toyota        → TOYOTA
Corolla XEI   → COROLLA XEI
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
- grupo e código do bem;
- CEP;
- UF;
- data de aquisição de bem;
- RENAVAM;
- placa;
- marca, modelo e ano de fabricação;
- estrutura mínima do JSON canônico.

---

## Testes automatizados

Para rodar todos:

```bash
python3 tests/run_tests.py
```

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
```

---

## Ferramentas principais

### `tools/normalize.py`

Funções de normalização:

- CPF/CNPJ;
- nomes;
- datas;
- valores monetários.

### `tools/agent_simulator.py`

Protótipo local de comportamento de agente.

Recebe texto bruto, chama o classificador simples e retorna:

- classificação provável;
- confiança;
- decisão de continuar ou não;
- schema recomendado;
- próximo passo sugerido.

### `tools/classify_document.py`

Classificador simples por palavras-chave.

### `tools/validate_config.py`

Valida o arquivo `config/project_config.json`.

### `tools/validate_extracted.py`

Valida extrações estruturadas.

### `tools/build_canonical_json.py`

Converte uma extração validada em JSON canônico parcial.

### `tools/pipeline_batch.py`

Processa várias extrações e consolida em um único JSON canônico.

### `tools/report.py`

Gera relatório humano em Markdown.

### `tools/run_project.py`

Comando principal do projeto.

### `tools/clean_outputs.py`

Remove outputs conhecidos.

### `tools/dev_check.py`

Roda validação da configuração, limpeza de outputs, pipeline principal e testes automatizados.

---

## Skill

A pasta `skill/` contém a documentação e contratos internos da skill.

```text
skill/
├── SKILL.md
├── instructions.md
├── references/
│   ├── codigos_bens.md
│   ├── codigos_pagamentos.md
│   ├── json_canonico.md
│   ├── pipeline.md
│   └── tipos_documentos.md
└── schemas/
    ├── canonical_irpf_2026.json
    ├── extracted_bem_imovel.json
    ├── extracted_bem_veiculo.json
    ├── extracted_informe_pj.json
    ├── extracted_plano_saude.json
    ├── extracted_recibo_medico.json
    └── project_config.json
```

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

Antes de commitar, sempre rode:

```bash
python3 tools/dev_check.py
```

---

## Histórico de mudanças

O histórico das principais etapas implementadas está em:

```text
CHANGELOG.md
```

---

## Próximas etapas planejadas

1. Melhorar o simulador local de agente.
2. Melhorar o classificador simples de documentos.
3. Preparar OCR real.
4. Criar camada de leitura de PDF/imagem.
5. Criar builder `.DEC` experimental.
6. Criar parser reverso `.DEC`.
7. Expandir suporte a dependentes, investimentos e outros rendimentos.
8. Criar testes adicionais para novos documentos.
9. Melhorar schemas formais.
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

O projeto segue a ideia:

```text
OCR é probabilístico.
Classificação inicial pode ser probabilística ou heurística.
Validação e geração de saída devem ser determinísticas.
```

Por isso, o fluxo nunca deve ser:

```text
documento → .DEC
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
