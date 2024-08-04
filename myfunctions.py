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
    Date: str = "19001231"
    Timekeeper: str = "DCRA"
    Client: int = 0
    Matter: int = 0
    Task: str = " "
    Activity: str = " "
    Billable: str = " "
    HoursWorked: float = 0
    HoursBilled: float = 0
    Rate: str = ""
    Amount: str = ""
    Phase: str = ""
    Code1: str = ""
    Code2: str = ""
    Code3: str = ""
    Note: str = ""
    Narrative: str = ""
    Body: str = ""
    Subject: str = ""
    Alias: str = ""


    

def generateNarrative(docs):
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo-16k")
    prompt_template = """Prepare a billing entry for attorney Daniel Cravens that succinctly summarizes the work that he performed. You must begin your billing entry with a verb. Where the work performed was a communication with another person, you should begin the billing entry with "Email communication with [person that Daniel was emailing] concerning [description of work]. You will infer the work performed from the following email: "{text}"
        Description: """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    output_summary = chain.run(docs)
    return output_summary

def GetClientDictionary():
    ClientDict = pd.read_excel(r"G:\Data\clientdata.xlsx")
    return ClientDict

def GetAliasesList():
    clientData = GetClientDictionary()
    clientDict = clientData.to_dict('split')
    aliasesList = clientData.to_dict('list')['Name']
    aliasesList.insert(0,"None")
    return aliasesList

def GetAliasesString():
    AliasesList = GetAliasesList()
    delimiter = ", "
    return delimiter.join(AliasesList)

def generateClientAlias(docs):
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo-16k")
    AliasesString = GetAliasesString()

# Define template

    template_string = "Infer the ALIAS from the body and subject of the following email: {text} as compared to the following list of aliases. Your response MUST be taken from the following list of aliases. Just respond with the alias without adding any additional comments.  For example, you may infer the  alias: Page v. Topix Pharmaceuticals where the body of the email refers to a person named Page. For example, you may infer the alias: Aguilera v. Turner Systems, Inc. where the subject of the email refers to Turner Systems. However, if you cannot infer a match, return None. ALIASES = " + AliasesString

    prompt = PromptTemplate.from_template(template_string)
    
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    output_clientmatter = chain.run(docs)
    print("Generated Alias: ", output_clientmatter)
    return output_clientmatter

def ConvertDate(year, month, day):
    yearstr = "{:04d}".format(year)
    monthstr = "{:02d}".format(month)
    daystr = "{:02d}".format(day)
    datestr = yearstr+monthstr+daystr
    return datestr

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
    te.Date = ConvertDate(msg.date.year, msg.date.month, msg.date.day)
    te.Client = ""
    te.Matter = ""
    return te


