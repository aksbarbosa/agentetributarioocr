import json
import sys
from pathlib import Path


DOCUMENT_TYPES = {
    "informe_rendimentos_pj": {
        "label": "Informe de rendimentos PJ",
        "keywords": [
            "INFORME DE RENDIMENTOS",
            "INFORME DE RENDIMENTOS PJ",
            "RENDIMENTOS TRIBUTAVEIS",
            "RENDIMENTOS TRIBUTÁVEIS",
            "FONTE PAGADORA",
            "CNPJ DA FONTE PAGADORA",
            "CNPJ DO PAGADOR",
            "PREVIDENCIA OFICIAL",
            "PREVIDÊNCIA OFICIAL",
            "IMPOSTO DE RENDA RETIDO NA FONTE",
            "IRRF",
            "DECIMO TERCEIRO",
            "DÉCIMO TERCEIRO",
            "IRRF SOBRE DECIMO TERCEIRO",
            "IRRF SOBRE DÉCIMO TERCEIRO",
        ],
    },
    "recibo_medico": {
        "label": "Recibo médico",
        "keywords": [
            "RECIBO MEDICO",
            "RECIBO MÉDICO",
            "MEDICO",
            "MÉDICO",
            "CRM",
            "PACIENTE",
            "NOME DO PACIENTE",
            "NOME DO MÉDICO",
            "NOME DO MEDICO",
            "CONSULTA",
            "SERVICO MEDICO",
            "SERVIÇO MÉDICO",
            "SERVICOS MEDICOS",
            "SERVIÇOS MÉDICOS",
            "VALOR TOTAL",
            "DATA DO PAGAMENTO",
        ],
    },
    "plano_saude": {
        "label": "Plano de saúde",
        "keywords": [
            "PLANO DE SAUDE",
            "PLANO DE SAÚDE",
            "PLANOS DE SAUDE",
            "PLANOS DE SAÚDE",
            "OPERADORA",
            "CNPJ DA OPERADORA",
            "BENEFICIARIO",
            "BENEFICIÁRIO",
            "VALOR PAGO",
            "VALOR NAO DEDUTIVEL",
            "VALOR NÃO DEDUTÍVEL",
            "COMPROVANTE DE PAGAMENTO PLANO DE SAUDE",
            "COMPROVANTE DE PAGAMENTO PLANO DE SAÚDE",
            "UNIMED",
            "COPARTICIPACAO",
            "COPARTICIPAÇÃO",
            "VALOR TOTAL DA NOTA FISCAL",
            "VALOR LÍQUIDO DA NOTA FISCAL",
            "PRESTADOR DE SERVIÇOS",
            "TOMADOR DE SERVIÇOS",
        ],
    },
    "bem_imovel": {
        "label": "Bem imóvel",
        "keywords": [
            "BEM IMOVEL",
            "BEM IMÓVEL",
            "IMOVEL",
            "IMÓVEL",
            "IPTU",
            "MATRICULA",
            "MATRÍCULA",
            "INSCRICAO IMOBILIARIA",
            "INSCRIÇÃO IMOBILIÁRIA",
            "LOGRADOURO",
            "BAIRRO",
            "MUNICIPIO",
            "MUNICÍPIO",
            "CIDADE",
            "CEP",
            "VALOR ANTERIOR",
            "VALOR ATUAL",
            "DATA DE AQUISICAO",
            "DATA DE AQUISIÇÃO",
        ],
    },
    "bem_veiculo": {
        "label": "Bem veículo",
        "keywords": [
            "BEM VEICULO",
            "BEM VEÍCULO",
            "DOCUMENTO DE VEICULO",
            "DOCUMENTO DE VEÍCULO",
            "VEICULO",
            "VEÍCULO",
            "RENAVAM",
            "PLACA",
            "MARCA",
            "MODELO",
            "ANO FABRICACAO",
            "ANO FABRICAÇÃO",
            "CRLV",
            "VALOR DO BEM",
            "VALOR ANTERIOR",
            "VALOR ATUAL",
            "DATA DE AQUISICAO",
            "DATA DE AQUISIÇÃO",
        ],
    },
}


TRANSPORT_DOCUMENT_KEYWORDS = [
    "CT-E",
    "CTE",
    "DACTE",
    "TRANSPORTADORA",
    "TRANSPORTE RODOVIARIO",
    "TRANSPORTE RODOVIÁRIO",
    "TRANSPORTE RODOVIARIO DE CARGAS",
    "TRANSPORTE RODOVIÁRIO DE CARGAS",
    "REMETENTE",
    "DESTINATARIO",
    "DESTINATÁRIO",
    "TOMADOR DO SERVICO",
    "TOMADOR DO SERVIÇO",
    "CARGAS",
    "CONHECIMENTO DE TRANSPORTE",
    "PROTOCOLO DE AUTORIZACAO",
    "PROTOCOLO DE AUTORIZAÇÃO",
]


def normalize_text(text: str) -> str:
    """
    Normaliza texto para classificação simples por palavras-chave.
    """
    return (text or "").upper()


def looks_like_transport_document(text: str) -> bool:
    """
    Detecta documentos de transporte, como DACTE/CT-e.

    Esses documentos não pertencem aos tipos fiscais pessoais atualmente
    suportados pelo projeto e devem ser classificados como desconhecidos.
    """
    upper = normalize_text(text)

    matches = sum(1 for keyword in TRANSPORT_DOCUMENT_KEYWORDS if keyword in upper)

    return matches >= 3


def empty_score_dict() -> dict:
    """
    Cria dicionário de scores zerados para todos os tipos conhecidos.
    """
    return {document_type: 0 for document_type in DOCUMENT_TYPES}


def empty_matched_keywords_dict() -> dict:
    """
    Cria dicionário de keywords encontradas vazio para todos os tipos conhecidos.
    """
    return {document_type: [] for document_type in DOCUMENT_TYPES}


def build_unknown_result(scores: dict | None = None, matched_keywords: dict | None = None) -> dict:
    """
    Resultado padrão para documento desconhecido.
    """
    if scores is None:
        scores = empty_score_dict()

    if matched_keywords is None:
        matched_keywords = empty_matched_keywords_dict()

    best_score = max(scores.values()) if scores else 0

    ranked_scores = sorted(scores.values(), reverse=True)
    second_score = ranked_scores[1] if len(ranked_scores) > 1 else 0

    return {
        "document_type": "desconhecido",
        "label": "Documento desconhecido",
        "confidence": "low",
        "scores": scores,
        "matched_keywords": matched_keywords,
        "best_score": best_score,
        "second_score": second_score,
    }


def score_document_type(text: str, document_type: str) -> tuple[int, list[str]]:
    """
    Calcula score simples por presença de palavras-chave.
    """
    upper = normalize_text(text)
    keywords = DOCUMENT_TYPES[document_type]["keywords"]

    matched_keywords = []

    for keyword in keywords:
        if keyword in upper:
            matched_keywords.append(keyword)

    return len(matched_keywords), matched_keywords


def confidence_from_scores(best_score: int, second_score: int) -> str:
    """
    Define confiança com base no score e na diferença para o segundo colocado.
    """
    if best_score <= 0:
        return "low"

    if best_score >= 4 and best_score >= second_score + 2:
        return "high"

    if best_score >= 2 and best_score > second_score:
        return "medium"

    return "low"


def classify_document_text(text: str) -> dict:
    """
    Classifica texto em um dos tipos suportados pelo projeto.

    Retorna documento desconhecido quando:
    - o texto está vazio;
    - parece ser documento de transporte;
    - nenhum tipo suportado tem score suficiente.
    """
    if not text or not text.strip():
        return build_unknown_result()

    if looks_like_transport_document(text):
        return build_unknown_result()

    scores = {}
    matched_keywords = {}

    for document_type in DOCUMENT_TYPES:
        score, matches = score_document_type(text, document_type)
        scores[document_type] = score
        matched_keywords[document_type] = matches

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    best_type, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    confidence = confidence_from_scores(best_score, second_score)

    if confidence == "low":
        return build_unknown_result(scores, matched_keywords)

    return {
        "document_type": best_type,
        "label": DOCUMENT_TYPES[best_type]["label"],
        "confidence": confidence,
        "scores": scores,
        "matched_keywords": matched_keywords,
        "best_score": best_score,
        "second_score": second_score,
    }


def classify_document_file(input_path: str) -> dict:
    """
    Classifica arquivo de texto.
    """
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    text = path.read_text(encoding="utf-8")

    return classify_document_text(text)


def print_human_result(result: dict, input_path: str | None = None) -> None:
    """
    Imprime resultado em formato humano.
    """
    if input_path:
        print(f"Arquivo: {input_path}")

    print(f"document_type: {result['document_type']}")
    print(f"label: {result['label']}")
    print(f"confidence: {result['confidence']}")
    print(f"best_score: {result['best_score']}")
    print(f"second_score: {result['second_score']}")
    print("")
    print("Scores:")

    for document_type, score in result["scores"].items():
        print(f"- {document_type}: {score}")

    print("")
    print("Palavras-chave encontradas:")

    for document_type, keywords in result["matched_keywords"].items():
        if keywords:
            joined = ", ".join(keywords)
        else:
            joined = "-"

        print(f"- {document_type}: {joined}")


def parse_args(argv: list[str]) -> tuple[str, bool]:
    """
    Uso:
        python3 tools/classify_document.py arquivo.txt
        python3 tools/classify_document.py arquivo.txt --json
    """
    if len(argv) < 2:
        print("Uso:")
        print("python3 tools/classify_document.py arquivo.txt")
        print("python3 tools/classify_document.py arquivo.txt --json")
        sys.exit(1)

    input_path = argv[1]
    print_json = "--json" in argv[2:]

    return input_path, print_json


def main() -> None:
    input_path, should_print_json = parse_args(sys.argv)

    result = classify_document_file(input_path)

    if should_print_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human_result(result, input_path)


if __name__ == "__main__":
    main()