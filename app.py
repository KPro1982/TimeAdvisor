# pip install streamlit langchain lanchain-openai beautifulsoup4 python-dotenv chromadb# pip install streamlit langchain lanchain-openai beautifulsoup4 python-dotenv chromadb
import streamlit as st
import extract_msg
import os

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_openai import ChatOpenAI

from langchain.chat_models import ChatOpenAI

from langchain.chains.summarize import load_summarize_chain

from langchain.docstore.document import Document

from langchain import OpenAI

from os import listdir
from os.path import join, isfile


load_dotenv()

# Set up LLM
llm = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo-16k")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# UI

st.set_page_config(page_title="TimeAdvisor")

st.title("Time Advisor")

def process_email(email):
    st.write("filename:", email.name)
    msg = extract_msg.openMsg(email)
    prompt_template = """Prepare a billing entry for attorney Daniel Cravens that succinctly summarizes the work that he performed. You must begin your billing entry with a verb. Where the work performed was a communication with another person, you should begin the billing entry with "Email communication with [person that Daniel was emailing] concerning [description of work]. You will infer the work performed from the following email: "{text}"
      Description: """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    doc = Document(msg.body)
    description = chain.run(doc)
    st.write("Summary", description)




uploaded_emails = st.file_uploader("Select Email to Process",  accept_multiple_files=True, help="emails to summarizes")
for email in uploaded_emails:
    process_email(email)

    






def get_response(query, chat_history):
    template = """
        You are a helpful assistant. Answer the following questions considering the history of the conversation:

        Chat history: {chat_history}
        User question: {user_question}

        """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI()
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
            "chat_history": chat_history,
            "user_question": query


        })

for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    else:
        with st.chat_message("AI"):
            st.markdown(message.content)




user_query = st.chat_input("Your message")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):       
        ai_response = st.write_stream(get_response(user_query, st.session_state.chat_history))

