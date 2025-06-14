from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import streamlit as st

# Load environment variables from .env file
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

llm_name = "gpt-3.5-turbo"
model = ChatOpenAI(api_key=openai_key, model=llm_name)

# then let's add some pre and sufix prompt
CSV_PROMPT_PREFIX = """
First set the pandas display options to show all the columns,
get the column names, then answer the question.
"""

CSV_PROMPT_SUFFIX = """
- **ALWAYS** before giving the Final Answer, try another method.
Then reflect on the answers of the two methods you did and ask yourself
if it answers correctly the original question.
If you are not sure, try another method.
FORMAT 4 FIGURES OR MORE WITH COMMAS.
- If the methods tried do not give the same result,reflect and
try again until you have two methods that have the same result.
- If you still cannot arrive to a consistent result, say that
you are not sure of the answer.
- If you are sure of the correct answer, create a beautiful
and thorough response using Markdown.
- **DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE,
ONLY USE THE RESULTS OF THE CALCULATIONS YOU HAVE DONE**.
- **ALWAYS**, as part of your "Final Answer", explain how you got
to the answer on a section that starts with: "\n\nExplanation:\n".
In the explanation, mention the column names that you used to get
to the final answer.
"""


st.title("CSV AI Agent with LangChain")

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    
    st.write("### Dataset Preview")
    
    df = pd.read_csv(uploaded_file)
    st.write(df.head())

    agent = create_pandas_dataframe_agent(
        llm=model,
        df=df,
        verbose=True,
    )
    
    if st.button("Explain Data"):
        data_query = "Explain the data in the csv. Explain what the dataset is about. Display the column names etc"
        data_explain = agent.invoke(data_query)
        st.write("### Explanation")
        st.markdown(data_explain["output"])
    else:
        pass
    

    # User input for the question
    st.write("### Ask a Question")
    question = st.text_input(
        "Enter your question about the dataset:",
        "",
    )

    # Run the agent and display the result
    if st.button("Run Query"):
        QUERY = CSV_PROMPT_PREFIX + question + CSV_PROMPT_SUFFIX
        res = agent.invoke(QUERY)
        st.write("### Final Answer")
        st.markdown(res["output"])