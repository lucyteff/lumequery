
import json
from src.ai.gemini_client import generate_text


def fallback_insights(question, query_result):
    rows = query_result["rows"]

    if not rows:
        return "A consulta não retornou resultados para análise."

    first_row = rows[0]
    values = ", ".join(
        f"{key}: {value}" for key, value in first_row.items()
    )

    return (
        "A análise automática por IA está temporariamente indisponível.\n\n"
        f"Foram encontrados {query_result['row_count']} registros.\n\n"
        f"Primeiro resultado: {values}"
    )


def run_insights_agent(question, query_result):
    data = {
        "question": question,
        "columns": query_result["columns"],
        "rows": query_result["rows"][:30],
        "total_rows": query_result["row_count"],
    }

    prompt = f"""
You are the Business Insights Agent of LumeQuery.
Analyze the SQL results and answer the user's business question.

Rules:
- Detect the language of the user's question.
- Answer in the same language as the user's question.
- If the question is in Portuguese, answer in Brazilian Portuguese.
- If the question is in English, answer in English.
- If the question is in Spanish, answer in Spanish.
- For any other language, answer in that language whenever possible.
- Use only the supplied data.
- Do not invent values or conclusions.
- Highlight relevant metrics and patterns.
- Be concise and objective.
- If the data is insufficient, say so.

Data:
{json.dumps(data, default=str, ensure_ascii=False)}
"""

    try:
        return generate_text(prompt)
    except Exception as error:
        if any(code in str(error) for code in ("503", "504", "429")):
            return fallback_insights(question, query_result)
        raise
