import json
import sys
from pathlib import Path

from classify_document import classify_document_file


SCHEMA_BY_DOCUMENT_TYPE = {
    "informe_rendimentos_pj": "skill/schemas/extracted_informe_pj.json",
    "recibo_medico": "skill/schemas/extracted_recibo_medico.json",
    "plano_saude": "skill/schemas/extracted_plano_saude.json",
    "bem_imovel": "skill/schemas/extracted_bem_imovel.json",
    "bem_veiculo": "skill/schemas/extracted_bem_veiculo.json",
}


NEXT_STEP_BY_DOCUMENT_TYPE = {
    "informe_rendimentos_pj": (
        "Criar uma extração estruturada JSON com os campos do informe de rendimentos PJ "
        "e depois validar com tools/validate_extracted.py."
    ),
    "recibo_medico": (
        "Criar uma extração estruturada JSON com os campos do recibo médico "
        "e depois validar com tools/validate_extracted.py."
    ),
    "plano_saude": (
        "Criar uma extração estruturada JSON com os campos do plano de saúde "
        "e depois validar com tools/validate_extracted.py."
    ),
    "bem_imovel": (
        "Criar uma extração estruturada JSON com os campos do bem imóvel "
        "e depois validar com tools/validate_extracted.py."
    ),
    "bem_veiculo": (
        "Criar uma extração estruturada JSON com os campos do veículo "
        "e depois validar com tools/validate_extracted.py."
    ),
    "desconhecido": (
        "Revisar o texto bruto, melhorar a extração OCR ou classificar manualmente o documento."
    ),
}


def build_agent_response(input_path: str) -> dict:
    """
    Simula a primeira decisão de um agente.

    Entrada:
        arquivo de texto bruto

    Saída:
        decisão estruturada com document_type provável,
        confiança, schema recomendado e próximo passo.
    """
    classification = classify_document_file(input_path)

    document_type = classification["document_type"]

    schema_path = SCHEMA_BY_DOCUMENT_TYPE.get(document_type)
    next_step = NEXT_STEP_BY_DOCUMENT_TYPE.get(
        document_type,
        NEXT_STEP_BY_DOCUMENT_TYPE["desconhecido"]
    )

    should_continue = (
        document_type != "desconhecido"
        and classification["confidence"] in {"high", "medium"}
    )

    return {
        "input_path": input_path,
        "classification": classification,
        "decision": {
            "document_type": document_type,
            "confidence": classification["confidence"],
            "should_continue": should_continue,
            "schema_path": schema_path,
            "next_step": next_step
        }
    }


def print_human_response(response: dict) -> None:
    """
    Mostra a resposta em formato humano.
    """
    classification = response["classification"]
    decision = response["decision"]

    print("Simulação do agente")
    print("")
    print(f"Arquivo analisado: {response['input_path']}")
    print("")
    print("Classificação:")
    print(f"- document_type: {classification['document_type']}")
    print(f"- label: {classification['label']}")
    print(f"- confidence: {classification['confidence']}")
    print(f"- best_score: {classification.get('best_score')}")
    print(f"- second_score: {classification.get('second_score')}")
    print("")

    print("Decisão:")
    print(f"- Deve continuar: {decision['should_continue']}")
    print(f"- Schema recomendado: {decision['schema_path']}")
    print(f"- Próximo passo: {decision['next_step']}")
    print("")

    print("Pontuação por tipo:")
    for document_type, score in sorted(
        classification["scores"].items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(f"- {document_type}: {score}")

    print("")
    print("Palavras-chave encontradas:")
    for document_type, keywords in sorted(
        classification["matched_keywords"].items(),
        key=lambda item: classification["scores"][item[0]],
        reverse=True
    ):
        if keywords:
            print(f"- {document_type}: {', '.join(keywords)}")


def print_json_response(response: dict) -> None:
    """
    Mostra a resposta em JSON.
    """
    print(json.dumps(response, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> tuple[str, bool]:
    """
    Uso:
        python3 tools/agent_simulator.py arquivo.txt
        python3 tools/agent_simulator.py arquivo.txt --json
    """
    if len(argv) not in {2, 3}:
        print("Uso:")
        print("python3 tools/agent_simulator.py caminho/do/texto.txt")
        print("python3 tools/agent_simulator.py caminho/do/texto.txt --json")
        sys.exit(1)

    input_path = argv[1]
    output_json = False

    if len(argv) == 3:
        if argv[2] != "--json":
            print("Argumento inválido.")
            print("Use --json para saída estruturada.")
            sys.exit(1)

        output_json = True

    file_path = Path(input_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    return input_path, output_json


def main() -> None:
    input_path, output_json = parse_args(sys.argv)

    response = build_agent_response(input_path)

    if output_json:
        print_json_response(response)
    else:
        print_human_response(response)

    if response["decision"]["document_type"] == "desconhecido":
        sys.exit(1)


if __name__ == "__main__":
    main()
