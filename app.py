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
import myfunctions

from myfunctions import process_email
from myfunctions import timeEntry
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

st.set_page_config(
    page_title="TimeAdvisor", 
    page_icon=None, 
    layout="wide", 
    menu_items=None
    )

def ValidateIndex(x):
    if(st.session_state.entryIndex + x <= 0):
        st.session_state.entryIndex = 0
    elif(st.session_state.entryIndex + x >= len(st.session_state.timeEntries)-1):
         st.session_state.entryIndex = len(st.session_state.timeEntries)-1
    else:
       st.session_state.entryIndex = st.session_state.entryIndex + x 


clientAliases = ['None','Aguilera v. Turner Systems, Inc.', 'Alvarez v. Command Security Services', 'Barnwell v. Gilton Solid Waste Management', 'Bhatia v. Mojio', 'Buksh v. Sixt Rent A Car', 'CAB v. UNITED SITE SERVICES, INC.', 'Casbeer v. Friends of Downtown SLO', 'Castellanos v. Urners, Inc.', 'Clement v. Rescue Mission Alliance', 'Cooper Aerial - PSG Contract Review', 'Crowe v. Alternative Power Generation', 'Deus v. Cuvaison, Inc.', 'Diaz v. Smartlink', 'Ghasemi v Valentia Analytical', 'Gonzalez Davalos v. Nouveau Bakery LLC', 'Gonzalez v. DS Electric, Inc.', 'Hernandez v. TSM Insurance Services', 'Hernandez v. Zarate Foods', 'Hicks v. SSA Group, LLC', 'Jackson v. Mental Health Systems dba TURN', 'Jermane v. Bethany Home Society of San Joaquin', 'Jimenez v. Wade et al ', 'Kolkmann v. Alternative Power Generation', 'Kumar DLSE De Novo Appeals', 'Melendez v. Peters Fruit Farms, Inc.', 'Miller v. Urata & Sons Concrete', 'Olson v. Allen Property Group, Inc.', 'Oracle Anesthesia, Inc. v. Central Valley Anesthesia Partners', 'Page v. Topix Pharmaceuticals', 'Patterson Board v. DCARA', 'PCC v. Fisher Construction Group', 'Raj v. WFP Hospitality II LLC', 'Rentner v. Trimble, Fletchers', 'Rocio Tafoya v. Peters Fruit Farms, Inc.', 'SBM v. Baker', 'Spooner v. Tri-Ced Economic Development Corporation', 'Staedler v. SSA Group, LLC', 'Steve v. Tulare Firestone, Inc.', 'Sweet Adeline v. Tasty Wings', 'TGS Logistics v. PCC Logistics', 'Thomas v. US Tech, Quest Media', 'Turpin v. Sinclair Broadcast Group, Inc.', 'Vaughn v. United Freight Lines', 'Wang et al v. Harris et al.', 'Webb v. Doug Tauzer Construction', 'White v. Andys Produce Market', 'Wood v. Smartlink']


if 'entryIndex' not in st.session_state:
    st.session_state.entryIndex = 0

if 'timeEntries' not in st.session_state:
    st.session_state.timeEntries = []

# load the openai_api key
openai_api_key = st.secrets["OpenAI_key"]

datafileName = ""


tab1, tab2, tab3 = st.tabs(["Config", "Review", "Submit"])





with tab1:
    st.subheader("DATAFILE", divider=True)
    create_button = st.button("Create New")
    if (create_button):
        datafileName = st.text_input("Filename", "")
    append_button = st.button("Append Existing")
    st.text(datafileName)
    st.subheader("PROCESS EMAIL", divider=True)
    uploaded_emails = st.file_uploader(" ",accept_multiple_files=True, help="Drag and drop emails to process into time entries.")
    if (st.button("Process Email")):
        for email in uploaded_emails:
            st.session_state.timeEntries.append(process_email(email))



with tab2:
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        st.write("Entry # ", st.session_state.entryIndex, "out of ", len(st.session_state.timeEntries)-1)
        st.date_input("Date: ", value=st.session_state.timeEntries[st.session_state.entryIndex].Date)
        match = clientAliases.index(st.session_state.timeEntries[st.session_state.entryIndex].Alias)
        client_select_alias = st.selectbox(label="Client Alias Selector: ", options=clientAliases, index=match)
        narrative = st.text_area(label="Narrative: ", value=st.session_state.timeEntries[st.session_state.entryIndex].Narrative)
        st.number_input("Time Worked: ", min_value=0.0, max_value=8.0, step=0.1, format="%0.1f")

        buttoncol1, buttoncol2, buttoncol3 = st.columns([1, 3, 1], gap="small")

        with buttoncol1:
            st.button("Prev", on_click=ValidateIndex(-1))
        
        with buttoncol3:
            st.button("Next", on_click=ValidateIndex(+1))

    with col2:
        st.text_area("Subject:", value=st.session_state.timeEntries[st.session_state.entryIndex].Subject)
        st.text_area("Body", value=st.session_state.timeEntries[st.session_state.entryIndex].Body, height=450)

