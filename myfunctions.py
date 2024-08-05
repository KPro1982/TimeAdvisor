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
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import openai
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
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
    Record: bool = True


    

def generateNarrative(docs):
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo-16k")
    prompt_template = """Prepare a billing entry for attorney Daniel Cravens that succinctly summarizes the work that he performed. You must begin your billing entry with a verb. Where the work performed was a communication with another person, you should begin the billing entry with "Email communication with [person that Daniel was emailing] concerning [description of work]. You will infer the work performed from the following email: "{text}"
        Description: """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    output_summary = chain.run(docs)
    return output_summary

def GetClientData():
    ClientDict = pd.read_excel(r"G:\Data\clientdata.xlsx")
    return ClientDict

def GetClientDictionary():
    clientData = GetClientData()
    clientDict = clientData.to_dict('split')['data']
    return clientDict

def GetAliasesList():
    clientData = GetClientData()
    aliasesList = clientData.to_dict('list')['Name']
    aliasesList.insert(0,"None")
    return aliasesList

def GetMatterNumberList():
    clientData = GetClientData()
    matterList = clientData.to_dict('list')['Client/Matter Number']
    matterList.insert(0,"None")
    return matterList


def GetAliasesString():
    AliasesList = GetAliasesList()
    delimiter = ", "
    return delimiter.join(AliasesList)

def generateClientAlias(docs):
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo-16k")
    AliasesString = GetAliasesString()

# Define template

    template_string = """
    You are an attorney billing expert. Your job is to infer the client alias from the folowing email: {text} 
    
    In most cases, the subject of the email will contain the alias. In those cases you will compare the email subject with the LIST OF APPROVED ALIASES and return the alias FROM THE LIST OF APPROVED ALIASES that best matches the subject line. 

    For example, where the email subject is "topix -- quick questions", you would compare this to the list of approved aliases and infer that Page v. Topix Pharmaceuticals is the best fit for the alias because none of the other aliases contain the work topix.
    
    In some cases, the subject will not contain enough information to infer the alias. In those case, you will look at the body of the email for information that matches an alias FROM THE LIST OF APPROVED ALIASES. 
    Example 1: you may infer the  alias: Page v. Topix Pharmaceuticals where the body of the email refers to a person named Page. 
    Example 2: you may infer the alias: Aguilera v. Turner Systems, Inc. where the subject of the email refers to Turner.

    IMPORTANT: YOUR RESPONSE SHOULD NOT BE CONVERSATIONAL. YOUR REPSONSE ONLY CONTAIN THE ALIAS FROM THE LIST OF APPROVED ALIASES WITHOUT ANY ADDITIONAL WORDS. 

    INCORRECT response: Based on the information provided in the email, the inferred client alias is "Gonzalez v. DS Electric, Inc."
    CORRECT response: Gonzalez v. DS Electric, Inc.

    IMPORTANT: IF YOU CANNOT INFER AN ALIAS FROM THE CONTENT PROVIDED, YOUR MUST RESPOND WITH THE SINGLE WORD: None

    INCORRECT response: The inferred client alias from the email is None.
    CORRECT response: none

    THE LIST OF APPROVED ALIASES FOLLOWS = """ + AliasesString 




    prompt = PromptTemplate.from_template(template_string)
    
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    output_clientmatter = chain.run(docs)
    output = output_clientmatter.strip()
    return output

def ConvertDate(year, month, day):
    yearstr = "{:04d}".format(year)
    monthstr = "{:02d}".format(month)
    daystr = "{:02d}".format(day)
    datestr = yearstr+monthstr+daystr
    return datestr

def GetMatterIndex(alias):
    clientList = GetAliasesList()
    try:
        matterIndex = clientList.index(alias)
    except:
        matterIndex = 0
    return matterIndex
    


def GetClientMatterString(alias):
    matterIndex = GetMatterIndex(alias)
    clientMatterNumberList = GetMatterNumberList()
    clientMatterString = clientMatterNumberList[matterIndex]
    return clientMatterString

def GetClientFromAlias(alias):
    clientMatterString = GetClientMatterString(alias)
    if(clientMatterString.find('-') > -1):
        cmlist = clientMatterString.split("-")
        return cmlist[0]
    else:
        return 0

def GetMatterFromAlias(alias):
    clientMatterString = GetClientMatterString(alias)
    if(clientMatterString.find('-') > -1):
        cmlist = clientMatterString.split("-")
        return cmlist[1]
    else:
        return 0

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
    te.Client = GetClientFromAlias(te.Alias)
    te.Matter = GetMatterFromAlias(te.Alias)
    return te


