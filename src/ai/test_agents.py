
from src.ai.sql_agent import run_sql_agent
from src.ai.insights_agent import run_insights_agent


def main():
    question = "Quais foram os cinco restaurantes com maior número de pedidos?"

    query_result = run_sql_agent(question)
    insights = run_insights_agent(question, query_result)

    print("\nLUMEQUERY")
    print("=" * 50)

    print("\nSQL GENERATED:")
    print(query_result["sql"])

    print("\nDATABASE RESULTS:")
    for row in query_result["rows"]:
        print(row)

    print("\nBUSINESS INSIGHTS:")
    print(insights)


if __name__ == "__main__":
    main()
