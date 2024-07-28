# pip install -r requirements.txt
# pip freeze > requirements.txt

# Import all of the modules used by the code

import streamlit as st
import extract_msg
import os
import textwrap
import csv

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_community.document_loaders import OutlookMessageLoader

from langchain_openai import ChatOpenAI

from langchain.chat_models import ChatOpenAI

from langchain.chains.summarize import load_summarize_chain

from langchain.docstore.document import Document

from langchain import OpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter

from os import listdir
from os.path import join, isfile

from pathlib import Path

# load the openai_api key

load_dotenv()

# choose llm and temperature

llm = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo-16k")

# set up UI using streamlit. st = streamlit

st.set_page_config(page_title="TimeAdvisor")
st.title("Time Advisor")
datafileName = ""

with st.sidebar:
    st.subheader("DATAFILE", divider=True)
    col1, col2 = st.columns(2)

    with col1:
        create_button = st.button("Create New")
        if (create_button):
            datafileName = st.text_input("Filename", "")
        append_button = st.button("Append Existing")

    with col2:
        st.text(datafileName)

    

    st.subheader("PROCESS EMAIL", divider=True)
    uploaded_emails = st.file_uploader(" ",accept_multiple_files=True, help="Drag and drop emails to process into time entries.")







def generateDescription(docs):
    prompt_template = """Prepare a billing entry for attorney Daniel Cravens that succinctly summarizes the work that he performed. You must begin your billing entry with a verb. Where the work performed was a communication with another person, you should begin the billing entry with "Email communication with [person that Daniel was emailing] concerning [description of work]. You will infer the work performed from the following email: "{text}"
        Description: """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    output_summary = chain.run(docs)
    description = textwrap.fill(output_summary, width=100)
    st.write("Time Entry: ", description)

def record_entry(entry):
    st.write(entry)


def process_email(email):
    msg = extract_msg.Message(email)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000, chunk_overlap=0, separators=[" ", ",", "\n"]
    )
    texts = text_splitter.split_text(msg.body)
 #   docs = [Document(page_content=t) for t in texts[:4]]
    docs = [Document(page_content=msg.body)]
    generateDescription(docs)













# st call creates the UI element for the drag and drop function


# loop to process the email dropped into UI
for email in uploaded_emails:
    process_email(email)  # calling the method defined above

    