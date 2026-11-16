
import pandas as pd
import streamlit as st

from src.ai.orchestrator import ask_lumequery


st.set_page_config(
    page_title="LumeQuery",
    page_icon="📊",
    layout="wide"
)

st.title("LumeQuery")
st.caption("AI-Powered Data Intelligence Platform")

st.write(
    "Ask questions about marketplace performance "
    "using natural language."
)

with st.form("question_form"):
    question = st.text_area(
        "Your business question",
        placeholder="Which restaurants have the highest number of orders?"
    )

    submitted = st.form_submit_button("Analyze")

if submitted:
    if not question.strip():
        st.warning("Enter a question to continue.")
    else:
        try:
            with st.spinner("Analyzing marketplace data..."):
                result = ask_lumequery(question)

            st.subheader("Business Insights")
            st.markdown(result["insights"])

            st.subheader("Query Information")
            col1, col2 = st.columns(2)

            col1.metric("Rows returned", result["row_count"])
            col2.write("**Generated SQL**")
            st.code(result["sql"], language="sql")

            st.subheader("Query Results")

            # Display the data returned by PostgreSQL
            query_result = pd.DataFrame(
                result.get("rows", [])
            )

            if not query_result.empty:
                st.dataframe(query_result, use_container_width=True)
            else:
                st.info("No records found.")

        except Exception as error:
            st.error(f"Analysis failed: {error}")
