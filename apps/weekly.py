import streamlit as st

from typing import cast, List
from github import Github, PullRequest, File

from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

st.header("Beacon > Codebase Analysis")
st.subheader("Kimley-Horn/SigOpsMetrics")

openai_token = st.secrets["openai_token"]

@st.cache_data
def get_pull_requests():
    g = Github()
    repo = g.get_repo("KimleyHorn/SigOpsMetrics")
    pulls = repo.get_pulls(state="closed")
    return [{
        "title": pull.title,
        "body": pull.body,
        "author": pull.user.login,
        "created_at": pull.created_at,
        "merged_at": pull.merged_at,
    } for pull in
        pulls.get_page(0)[0:100]
    ]

pr_data = ""
for pull in get_pull_requests():
    if not pull["merged_at"]:
        continue
    pr_data += f"""
    Title: {pull['title']}
    Body: {pull['body']}
    Author: {pull['author']}
    Created At: {pull['created_at'].strftime("%Y-%m-%d")}
    Merge Date: {pull['merged_at'].strftime("%Y-%m-%d")}
    \n
    """

llm = OpenAI(temperature=0.2, openai_api_key=openai_token)

input = st.text_input("Enter a question", value="How many pull requests were submitted by each engineer?")

@st.cache_data
def get_llm_response(data, question):
    prompt = f"""

    Act as an engineering manager explaining progress to a non-technical stakeholder.

    You are given a list of pull requests with the following information:
    Title, Body, Author, Merge Date 

    {data}

    Your task is to answer the following question:
    {question}

    Please deliver your response in two distinct sections.

    The first section should have the title of [Answer] and should contain the answer to the question.
    If the answer can be presented in a table, please return a markdown table.
    If the answer can be presented in a list, please return a markdown list.
    If you don't know the answer, please return "I don't know".

    The second section should have the title of [Explanation] and should contain a brief explanation of how you arrived at your answer.
    """
    return llm(prompt)

def q_and_a(question):
    header = question.strip().splitlines()[0]
    st.markdown(f"### {header}")
    st.markdown(get_llm_response(
        pr_data,
        question
    ))

q_and_a(input)
# q_and_a("""
# How many pull requests were submitted by each engineer?

# Return the results in a markdown table. 
# """)

# q_and_a("""
# How long was the average time to merge a pull request for each engineer?

# Return the results in a markdown table.
# """)