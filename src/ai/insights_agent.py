
import json

from src.ai.gemini_client import generate_text


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
- Answer in Brazilian Portuguese.
- Use only the supplied data.
- Do not invent values or conclusions.
- Highlight relevant metrics and patterns.
- Be concise and objective.
- If the data is insufficient, say so.

Data:
{json.dumps(data, default=str, ensure_ascii=False)}
"""

    return generate_text(prompt)
