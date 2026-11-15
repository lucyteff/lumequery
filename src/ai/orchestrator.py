
from src.ai.sql_agent import run_sql_agent
from src.ai.insights_agent import run_insights_agent


def ask_lumequery(question):
    # The orchestrator coordinates both specialized agents.
    query_result = run_sql_agent(question)

    insights = run_insights_agent(
        question,
        query_result
    )

    return {
        "question": question,
        "sql": query_result["sql"],
        "row_count": query_result["row_count"],
        "insights": insights,
    }
