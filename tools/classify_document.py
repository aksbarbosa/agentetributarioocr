import json
import sys
from pathlib import Path

from normalize import normalize_name


DOCUMENT_TYPE_LABELS = {
    "informe_rendimentos_pj": "Informe de rendimentos de pessoa jurídica",
    "recibo_medico": "Recibo médico",
    "plano_saude": "Informe de plano de saúde",
    "bem_imovel": "Bem imóvel",
    "bem_veiculo": "Bem veículo",
    "desconhecido": "Documento desconhecido",
}


KEYWORDS_BY_DOCUMENT_TYPE = {
    "informe_rendimentos_pj": [
        "INFORME DE RENDIMENTOS",
        "RENDIMENTOS TRIBUTAVEIS",
        "FONTE PAGADORA",
        "IMPOSTO DE RENDA RETIDO",
        "IRRF",
        "DECIMO TERCEIRO",
        "13",
        "CNPJ DA FONTE PAGADORA",
    ],
    "recibo_medico": [
        "RECIBO",
        "CONSULTA MEDICA",
        "MEDICO",
        "CRM",
        "PACIENTE",
        "HONORARIOS MEDICOS",
        "CPF DO PROFISSIONAL",
    ],
    "plano_saude": [
        "PLANO DE SAUDE",
        "OPERADORA",
        "ANS",
        "DESPESAS MEDICAS",
        "INFORME DE PAGAMENTOS",
        "VALOR PAGO AO PLANO",
    ],
    "bem_imovel": [
        "IPTU",
        "MATRICULA DO IMOVEL",
        "IMOVEL",
        "APARTAMENTO",
        "CASA",
        "TERRENO",
        "ENDERECO DO IMOVEL",
        "INSCRICAO IMOBILIARIA",
    ],
    "bem_veiculo": [
        "CRLV",
        "RENAVAM",
        "PLACA",
        "VEICULO",
        "AUTOMOVEL",
        "MARCA",
        "MODELO",
        "ANO FABRICACAO",
        "CERTIFICADO DE REGISTRO",
    ],
}


def normalize_text(text: str) -> str:
    """
    Normaliza texto para comparação simples por palavras-chave.
    """
    return normalize_name(text or "")


def score_document_type(text: str, keywords: list[str]) -> int:
    """
    Conta quantas palavras-chave aparecem no texto.
    """
    normalized_text = normalize_text(text)

    score = 0
    matched_keywords = []

    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)

        if normalized_keyword in normalized_text:
            score += 1
            matched_keywords.append(keyword)

    return score, matched_keywords


def classify_document_text(text: str) -> dict:
    """
    Classifica um texto bruto em um document_type conhecido.

    Retorna:
    - document_type
    - label
    - confidence
    - scores
    - matched_keywords
    """
    scores = {}
    matched_keywords_by_type = {}

    for document_type, keywords in KEYWORDS_BY_DOCUMENT_TYPE.items():
        score, matched_keywords = score_document_type(text, keywords)
        scores[document_type] = score
        matched_keywords_by_type[document_type] = matched_keywords

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    sorted_scores = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0

    if best_score == 0:
        return {
            "document_type": "desconhecido",
            "label": DOCUMENT_TYPE_LABELS["desconhecido"],
            "confidence": "low",
            "scores": scores,
            "matched_keywords": matched_keywords_by_type,
            "best_score": best_score,
            "second_score": second_score
        }

    if best_score >= 3 and best_score >= second_score + 2:
        confidence = "high"
    elif best_score >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "document_type": best_type,
        "label": DOCUMENT_TYPE_LABELS[best_type],
        "confidence": confidence,
        "scores": scores,
        "matched_keywords": matched_keywords_by_type,
        "best_score": best_score,
        "second_score": second_score
    }


def classify_document_file(path: str) -> dict:
    """
    Classifica um arquivo de texto.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    text = file_path.read_text(encoding="utf-8")

    return classify_document_text(text)


def print_classification_result(result: dict) -> None:
    """
    Imprime o resultado da classificação em formato humano.
    """
    print("Classificação do documento:")
    print(f"- document_type: {result['document_type']}")
    print(f"- label: {result['label']}")
    print(f"- confidence: {result['confidence']}")

    print("")
    print("Pontuação:")

    for document_type, score in sorted(
        result["scores"].items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(f"- {document_type}: {score}")

    print("")
    print("Palavras-chave encontradas:")

    for document_type, keywords in sorted(
        result["matched_keywords"].items(),
        key=lambda item: result["scores"][item[0]],
        reverse=True
    ):
        if not keywords:
            continue

        print(f"- {document_type}: {', '.join(keywords)}")


def print_json_result(result: dict) -> None:
    """
    Imprime o resultado da classificação em JSON.
    """
    print(json.dumps(result, ensure_ascii=False, indent=2))


def parse_args(argv: list[str]) -> tuple[str, bool]:
    """
    Interpreta argumentos de linha de comando.

    Uso:
        python3 tools/classify_document.py arquivo.txt
        python3 tools/classify_document.py arquivo.txt --json
    """
    if len(argv) not in {2, 3}:
        print("Uso:")
        print("python3 tools/classify_document.py caminho/do/texto.txt")
        print("python3 tools/classify_document.py caminho/do/texto.txt --json")
        sys.exit(1)

    input_path = argv[1]
    output_json = False

    if len(argv) == 3:
        if argv[2] != "--json":
            print("Argumento inválido.")
            print("Use --json para saída estruturada.")
            sys.exit(1)

        output_json = True

    return input_path, output_json


def main() -> None:
    input_path, output_json = parse_args(sys.argv)

    result = classify_document_file(input_path)

    if output_json:
        print_json_result(result)
    else:
        print_classification_result(result)

    if result["document_type"] == "desconhecido":
        sys.exit(1)


if __name__ == "__main__":
    main()
