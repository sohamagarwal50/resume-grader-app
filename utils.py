import PyPDF2
from docx import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic.v1 import BaseModel, Field
from typing_extensions import TypedDict
import os
import streamlit as st
os.environ['GOOGLE_API_KEY'] = st.secrets["GOOGLE_API_KEY"]
# LLM setup
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', temperature=0.0)

# State structure
class State(TypedDict):
    name : str
    contact_details:str
    resume_data : str
    skills: str
    education: str
    work_exp: str
    job_desc  : str
    qualifications : str
    resume_score : int
    reason: str
    projects: str
    positives:str
    negatives:str

class Score(BaseModel):
    score: int = Field(description="Similarity score from 0 to 100")
    reason: str = Field(description = "Give a detailed answer on why you gave such score to the resume")
    positives: str = Field(description="Give the positives in the person's resume which make him/her a good candidate.")
    negatives: str = Field(description = "Give the negatives in the person's resume which don't make him/her a good candidate.")

class ResumeBuilder(BaseModel):
    name : str = Field(description="Using the resume data identify the name of the person")
    contact_details:str=Field(description="Using the resume data extract the contact details of the person")
    skills: str = Field(description="Using the resume data build a list of skills this person has.")
    work_exp: str = Field(description="Using the resume data build a create a list of work experience this person has done.")
    education: str = Field(description="Using the resume data create a string of all educational data of this person")
    projects: str = Field(description = "Using the resume data create a list of all projects and their description this person has made")

def Builder(state: State):
    prompt = f'''You are a helpful AI Assistant. Your job is to create strings of data of name, contact details, skills, work experience, educational data and projects of a person using the person's resume data.
                Your created responses must be descriptive and must encapsulate all of the relevant details in the resume. If you don't find a particular category, state so.
                Here is the resume: {state["resume_data"]}'''
    model = llm.with_structured_output(ResumeBuilder)
    response = model.invoke(prompt)
    return {
        'name': response.name,
        'contact_details': response.contact_details,
        'skills': response.skills,
        'education': response.education,
        'work_exp': response.work_exp,
        'projects': response.projects
    }

def grader(state: State):
    prompt = f'''You are a helpful AI assistant. Your task is to give a score from 0–100. The important information from the resume has already been extracted.
                Use this to decide how suitable the candidate is for the job. You must be harsh and scrutinizing in your analysis as the user does not want any weak candidates.
    Skills: {state['skills']}
    Work Experience: {state['work_exp']}
    Education: {state['education']}
    Projects: {state['projects']}
    Job Description: {state['job_desc']}
    Qualifications: {state['qualifications']}'''
    model = llm.with_structured_output(Score)
    response = model.invoke(prompt)
    return {"resume_score": response.score, "reason": response.reason,"positives":response.positives,"negatives":response.negatives}

# Graph logic
memory = MemorySaver()
graph_builder = StateGraph(State)
graph_builder.add_node("Resume Builder", Builder)
graph_builder.add_node("Resume Grader", grader)
graph_builder.add_edge(START, "Resume Builder")
graph_builder.add_edge("Resume Builder", "Resume Grader")
graph_builder.add_edge("Resume Grader", END)
chain = graph_builder.compile(checkpointer=memory)

# File parsers
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])
