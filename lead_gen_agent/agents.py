from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent 
from pydantic import BaseModel
from tools import search_leads, scrape_lead_page
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

class Lead(BaseModel):  # This will return a clean structured object instead of messy output from the LLM
    company_name: str 
    website: str 
    contact_name: str 
    contact_title: str
    relevance_score: str
    score_reason: str 
    email_draft: str 

#Search Agent
def build_search_agent():   # function that buolds and returns search agent 
        return create_react_agent(   # builds react agent 
            model=llm,
            tools=[search_leads],   #uses search tool we created earlier
            prompt=(         #intruction for the  LLM 
                "You are a sales development researcher. Given an ICP, generate targeted search queries and use the search_leads tool to find matching companies and contracts and Run at least 3 different searches"
            )
        )
    
#Extractor Agent 
def build_extractor_agent():  #function 
        return create_react_agent( #react agent
            model=llm,
            tools=[scrape_lead_page],
            prompt=( #intstructions for the agent 
                "You are a lead research sepcialist, Given search results, pick the best URLs and use scrape_lead_page to extract company name, website decision-maker names and titles"
            )
        )
    
#Scorer Chain 
scorer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sales qualification expert. Extract and score leads against the ICP precisely."), #setting the ai's role 
    ("human", """                   
ICP : 
{icp} #filled with ideal customer profile 

Raw Lead Info:
{raw_lead_info} #filled in with the scraped comany info 

Return structured data for ONE company with:
- company_name, website, contact_name, contact_title
- relevance_score (1-10), score_reason (one sentence)
- email_draft (short cold email under 80 words)
""")
])

scorer_chain = scorer_prompt | llm.with_structured_output(Lead) #takes prompt and feeds it to the LLM, return data that matches lead

    
#Email Chain 
email_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert SDR who writes short, personalized cold emails that get replies."),
    ("human", """
Write a cold email for:
Company: {company_name}
Contact: {contact_name}, {contact_title}
Why they fit: {score_reason}

Under 80 words. Specific, human, soft CTA at the end.
""")
])

email_chain = email_prompt | llm | StrOutputParser() #converts LLM into plain text 