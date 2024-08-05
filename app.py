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
import time
import myfunctions

from myfunctions import process_email
from myfunctions import timeEntry
from myfunctions import GetAliasesList
from myfunctions import GetMatterFromAlias
from myfunctions import GetClientFromAlias


from enum import Enum
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import OutlookMessageLoader
from langchain_community.llms import openai
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from os import listdir
from os.path import join, isfile
from datetime import datetime
from pathlib import Path
from dataclasses import astuple, dataclass, field

st.set_page_config(
    page_title="TimeAdvisor", 
    page_icon=None, 
    layout="wide", 
    menu_items=None
    )

st.session_state.local_folder = "G:/Data/"


def ValidateIndex(x):
    maxx = len(st.session_state.timeEntries)-1
    timeWorked = 0.0
    if(st.session_state.entryIndex + x < 0):
        st.session_state.entryIndex = 0
    elif(st.session_state.entryIndex + x > maxx):
         st.session_state.entryIndex = maxx
    else:
       st.session_state.entryIndex = st.session_state.entryIndex + x 
    
def UpdateRecord(timeWorked, recordResult):
    print("UPDATE RECORD:", timeWorked, recordResult)
    alias = st.session_state.timeEntries[st.session_state.entryIndex].Alias 
    st.session_state.timeEntries[st.session_state.entryIndex].Client = GetClientFromAlias(alias)
    st.session_state.timeEntries[st.session_state.entryIndex].Matter = GetMatterFromAlias(alias)
    st.session_state.timeEntries[st.session_state.entryIndex].HoursWorked = timeWorked
    st.session_state.timeEntries[st.session_state.entryIndex].HoursBilled = timeWorked
    st.session_state.timeEntries[st.session_state.entryIndex].Record = recordResult
    timeWorked = 0




def DisplayReviewTab():
    recordResult = True
    timeWorked = 0.0
    if(len(st.session_state.timeEntries)>=1):
        col1, col2 = st.columns([1, 1], gap="small")
        with col1:
            bcol1, bcol2, bcol3, bcol4, bcol5 = st.columns([1, 1, 1, 1, 2], gap="small") 
            with bcol1:   
                st.button("Prev", key="PREV", on_click=ValidateIndex, args=(-1,))
                    
            with bcol2:
                st.button("Next", key="NEXT", on_click=ValidateIndex, args=(1,))
            
            with bcol4:
                recordResult = st.checkbox("Record", value=st.session_state.timeEntries[st.session_state.entryIndex].Record)
                st.session_state.timeEntries[st.session_state.entryIndex].Record = recordResult    
            with bcol5:
                st.write("Entry # ", st.session_state.entryIndex, "out of ", len(st.session_state.timeEntries)-1)

            clientAliases = GetAliasesList()
            st.text_input("Date: ", value=st.session_state.timeEntries[st.session_state.entryIndex].Date)

            try:
                match = clientAliases.index(st.session_state.timeEntries[st.session_state.entryIndex].Alias)
            except:                     
                print("Client alias not found")        # consider retrying lookup on failure
                match = 0

            client_select_alias = ""
            client_select_alias = st.selectbox(label="Client Alias Selector: ", options=clientAliases, index=match)
            st.session_state.timeEntries[st.session_state.entryIndex].Alias = client_select_alias 

            client = st.text_input(label="Client No.", value=GetClientFromAlias(client_select_alias))
            matter = st.text_input(label="Matter No.", value=GetMatterFromAlias(client_select_alias))


            narrative = st.text_area(label="Narrative: ", value=st.session_state.timeEntries[st.session_state.entryIndex].Narrative)

            timeWorked = st.session_state.timeEntries[st.session_state.entryIndex].HoursWorked
            timeWorked = st.number_input("Time Worked: ",value=float(timeWorked), min_value=0.0, max_value=8.0, step=0.1, format="%0.1f")
            st.session_state.timeEntries[st.session_state.entryIndex].Narrative = narrative


        with col2:
            st.text_area("Subject:", value=st.session_state.timeEntries[st.session_state.entryIndex].Subject)
            st.text_area("Body", value=st.session_state.timeEntries[st.session_state.entryIndex].Body, height=450)
        
        st.button("Update", on_click=UpdateRecord, args = (timeWorked,recordResult,))

if 'entryIndex' not in st.session_state:
    st.session_state.entryIndex = 0

if 'timeEntries' not in st.session_state:
    st.session_state.timeEntries = []

update_matter = False


# load the openai_api key
openai_api_key = st.secrets["OpenAI_key"]

datafileName = ""


configTab, reviewTab, submitTab = st.tabs(["Config", "Review", "Submit"])



def SetHome():
    st.session_state.local_folder = "G:/Data/"
    st.write("Configured for Home")


def SetWork():
    st.session_state.local_folder  = "c:/Users/dcravens/"
    st.write("Configured for Remote")

def SortFunction(te):
    return te.Date

with configTab:
    st.button("Home", on_click=SetHome)
    st.button("Remote", on_click=SetWork)
    st.subheader("PROCESS EMAIL", divider=True)
    uploaded_emails = st.file_uploader(" ",accept_multiple_files=True, help="Drag and drop emails to process into time entries.")
    if (st.button("Process Email")):
        emailcount = 0
        for email in uploaded_emails:
            st.session_state.timeEntries.append(process_email(email))
            uploaded_emails.remove(email)
            emailcount += 1
            st.write("processed:", emailcount, ":", email.name)
            if(emailcount % 5 == 0):
                print("Pausing.....")
                time.sleep(30)
                timestamp = datetime.strftime(datetime.now(),"%m-%d-%Y_%H-%M-%S")
                df = pd.DataFrame(st.session_state.timeEntries)
                file_name = st.session_state.local_folder + "TempTimeData.xlsx"
                print("Filename:", file_name)
                datatoexcel = pd.ExcelWriter(file_name, mode="a")                                             )
                df.to_excel(datatoexcel, index=False)
                datatoexcel.close()
                st.session_state.timeEntries.clear()
        st.write("processing completed!")


        

with reviewTab:
    DisplayReviewTab()

with submitTab:

    timestamp = datetime.strftime(datetime.now(),"%m-%d-%Y_%H-%M-%S")
    df = pd.DataFrame(st.session_state.timeEntries)
    if(st.button("Refresh")):
        edited_data = st.data_editor(df)

    if(st.button("Save")):
        file_name = st.session_state.local_folder + timestamp + "  TimeEntryData.xlsx"
        print("Filename:", file_name)
        datatoexcel = pd.ExcelWriter(file_name)
        df.to_excel(datatoexcel, index=False)
        datatoexcel.close()