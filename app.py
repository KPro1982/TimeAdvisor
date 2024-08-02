# pip install -r requirements.txt
# pip freeze > requirements.txt

# Import all of the modules used by the code

import streamlit as st
import extract_msg
import os
import textwrap
import csv
import datetime
import pandas as pd
from enum import Enum


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

from dataclasses import astuple, dataclass, field



# create data class

@dataclass
class timeEntry:
    UserID: str = "DCRA"
    Date: str = ""
    Timekeeper: str = "DCRA"
    # Client: int = 0
    # Matter: int = 0
    # Task: str = ""
    # Activity: str = ""
    # Billable: str = ""
    # HoursWorked: float = 0
    # HoursBilled: float = 0
    # Rate: str = ""
    # Amount: str = ""
    # Phase: str = ""
    # Code1: str = ""
    # Code2: str = ""
    # Code3: str = ""
    # Note: str = ""
    Narrative: str = ""
    Body: str = ""
    Subject: str = ""
    Alias: str = ""


clientAliases = ['None','Aguilera v. Turner Systems, Inc.', 'Alvarez v. Command Security Services', 'Barnwell v. Gilton Solid Waste Management', 'Bhatia v. Mojio', 'Buksh v. Sixt Rent A Car', 'CAB v. UNITED SITE SERVICES, INC.', 'Casbeer v. Friends of Downtown SLO', 'Castellanos v. Urners, Inc.', 'Clement v. Rescue Mission Alliance', 'Cooper Aerial - PSG Contract Review', 'Crowe v. Alternative Power Generation', 'Deus v. Cuvaison, Inc.', 'Diaz v. Smartlink', 'Ghasemi v Valentia Analytical', 'Gonzalez Davalos v. Nouveau Bakery LLC', 'Gonzalez v. DS Electric, Inc.', 'Hernandez v. TSM Insurance Services', 'Hernandez v. Zarate Foods', 'Hicks v. SSA Group, LLC', 'Jackson v. Mental Health Systems dba TURN', 'Jermane v. Bethany Home Society of San Joaquin', 'Jimenez v. Wade et al ', 'Kolkmann v. Alternative Power Generation', 'Kumar DLSE De Novo Appeals', 'Melendez v. Peters Fruit Farms, Inc.', 'Miller v. Urata & Sons Concrete', 'Olson v. Allen Property Group, Inc.', 'Oracle Anesthesia, Inc. v. Central Valley Anesthesia Partners', 'Page v. Topix Pharmaceuticals', 'Patterson Board v. DCARA', 'PCC v. Fisher Construction Group', 'Raj v. WFP Hospitality II LLC', 'Rentner v. Trimble, Fletchers', 'Rocio Tafoya v. Peters Fruit Farms, Inc.', 'SBM v. Baker', 'Spooner v. Tri-Ced Economic Development Corporation', 'Staedler v. SSA Group, LLC', 'Steve v. Tulare Firestone, Inc.', 'Sweet Adeline v. Tasty Wings', 'TGS Logistics v. PCC Logistics', 'Thomas v. US Tech, Quest Media', 'Turpin v. Sinclair Broadcast Group, Inc.', 'Vaughn v. United Freight Lines', 'Wang et al v. Harris et al.', 'Webb v. Doug Tauzer Construction', 'White v. Andys Produce Market', 'Wood v. Smartlink']



# load the openai_api key
openai_api_key = st.secrets["OpenAI_key"]


# choose llm and temperature

#llm = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo-16k", api_key=openai_api_key)

# set up UI using streamlit. st = streamlit


st.set_page_config(page_title="TimeAdvisor", page_icon=None, layout="centered", initial_sidebar_state="expanded", menu_items=None)
st.title("Time Advisor")
datafileName = ""

with st.sidebar:
    st.subheader("DATAFILE", divider=True)

    create_button = st.button("Create New")
    if (create_button):
        datafileName = st.text_input("Filename", "")
    append_button = st.button("Append Existing")


    st.text(datafileName)

    st.subheader("PROCESS EMAIL", divider=True)
    uploaded_emails = st.file_uploader(" ",accept_multiple_files=True, help="Drag and drop emails to process into time entries.")








def generateNarrative(docs):
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo-16k")
    prompt_template = """Prepare a billing entry for attorney Daniel Cravens that succinctly summarizes the work that he performed. You must begin your billing entry with a verb. Where the work performed was a communication with another person, you should begin the billing entry with "Email communication with [person that Daniel was emailing] concerning [description of work]. You will infer the work performed from the following email: "{text}"
        Description: """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    output_summary = chain.run(docs)
    return output_summary

def generateClientAlias(docs):
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo-16k")
    prompt_template_client = """Infer the ALIAS  from the body and subject of the following email: "{text}" as compared to the following list of aliases. Your response MUST be taken from the following list of aliases. Just respond with the alias without adding any additional comments.  For example, you may infer the  alias: Page v. Topix Pharmaceuticals where the body of the email refers to a person named Page. For example, you may infer the alias: Aguilera v. Turner Systems, Inc. where the subject of the email refers to 'Turner Systems'. However, if you cannot infer a match, return 'None'. ALIASES: 'None', Do NOT include any quotes in the resposne. 'Aguilera v. Turner Systems, Inc.', 'Alvarez v. Command Security Services', 'Barnwell v. Gilton Solid Waste Management', 'Bhatia v. Mojio', 'Buksh v. Sixt Rent A Car', 'CAB v. UNITED SITE SERVICES, INC.', 'Casbeer v. Friends of Downtown SLO', 'Castellanos v. Urners, Inc.', 'Clement v. Rescue Mission Alliance', 'Cooper Aerial - PSG Contract Review', 'Crowe v. Alternative Power Generation', 'Deus v. Cuvaison, Inc.', 'Diaz v. Smartlink', 'Ghasemi v Valentia Analytical', 'Gonzalez Davalos v. Nouveau Bakery LLC', 'Gonzalez v. DS Electric, Inc.', 'Hernandez v. TSM Insurance Services', 'Hernandez v. Zarate Foods', 'Hicks v. SSA Group, LLC', 'Jackson v. Mental Health Systems dba TURN', 'Jermane v. Bethany Home Society of San Joaquin', 'Jimenez v. Wade et al ', 'Kolkmann v. Alternative Power Generation', 'Kumar DLSE De Novo Appeals', 'Melendez v. Peters Fruit Farms, Inc.', 'Miller v. Urata & Sons Concrete', 'Olson v. Allen Property Group, Inc.', 'Oracle Anesthesia, Inc. v. Central Valley Anesthesia Partners', 'Page v. Topix Pharmaceuticals', 'Patterson Board v. DCARA', 'PCC v. Fisher Construction Group', 'Raj v. WFP Hospitality II LLC', 'Rentner v. Trimble, Fletchers', 'Rocio Tafoya v. Peters Fruit Farms, Inc.', 'SBM v. Baker', 'Spooner v. Tri-Ced Economic Development Corporation', 'Staedler v. SSA Group, LLC', 'Steve v. Tulare Firestone, Inc.', 'Sweet Adeline v. Tasty Wings', 'TGS Logistics v. PCC Logistics', 'Thomas v. US Tech, Quest Media', 'Turpin v. Sinclair Broadcast Group, Inc.', 'Vaughn v. United Freight Lines', 'Wang et al v. Harris et al.', 'Webb v. Doug Tauzer Construction', 'White v. Andys Produce Market', 'Wood v. Smartlink'"""

    prompt_clientmatter = PromptTemplate.from_template(prompt_template_client)
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt_clientmatter)
    output_clientmatter = chain.run(docs)
    return output_clientmatter

timeEntries = []  # This will contain all of the timeentries


def process_email(email):
    global timeEntries
    msg = extract_msg.Message(email)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000, chunk_overlap=0, separators=[" ", ",", "\n"]
    )
    texts = text_splitter.split_text(msg.body)
 #   docs = [Document(page_content=t) for t in texts[:4]]
    docs = [Document(page_content=msg.body)]
    te = timeEntry()
    narrative = generateNarrative(docs)
    te.Narrative = narrative
    te.Body = msg.body 
    te.Subject =  msg.subject
    docs = [Document(page_content=msg.body)]
    te.Alias = generateClientAlias(docs)
    te.Date = msg.date
    return te


# loop to process the email dropped into UI
for email in uploaded_emails:
    timeEntries.append(process_email(email))


with st.form(key="timeentry_form"):
    st.date_input("Date: ", value=timeEntries[0].Date)
    st.number_input("Time Worked: ", min_value=0.0, max_value=8.0, step=0.1, format="%0.1f")
    match = clientAliases.index(timeEntries[0].Alias)
    client_select_alias = st.selectbox(label="Client Alias Selector: ", options=clientAliases, index=match)
   # client_alias = st.text_input(label="Email Subject Line: ", value=timeEntries[0].Subject)
    narrative = st.text_area(label="Narrative: ", value=timeEntries[0].Narrative)
    submitButton = st.form_submit_button("Submit")
    
    #st.write("Body: ", timeEntries[0].Body)
           