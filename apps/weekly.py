import streamlit as st

from typing import cast, List
from github import Github, PullRequest, File

from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

st.header("Weekly Report")

openai_token = st.secrets["openai_token"]

with st.sidebar:
    st.title("Beacon")

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


@st.cache_data
def get_llm_response(data, task):
    prompt = f"""

    Act as an engineering manager explaining progress to a non-technical stakeholder.

    You are given a list of pull requests with the following information:
    Title, Body, Author, Merge Date 

    {data}

    Your task in the following:
    {task}
    """
    return llm(prompt)

def q_and_a(question):
    header = question.strip().splitlines()[0]
    st.markdown(f"### {header}")
    st.markdown(get_llm_response(
        pr_data,
        question
    ))

q_and_a("""
For each engineer, write up a brief summary of their contributions for the week.

Return the results in a markdown table. 
""")

q_and_a("""
How many pull requests were submitted by each engineer?

Return the results in a markdown table. 
""")

q_and_a("""
How long was the average time to merge a pull request for each engineer?

Return the results in a markdown table.
""")