# Lead Generation Agent

A multi-agent AI pipeline that automates lead research for sales teams.

## What it does
- Searches the web for companies matching an ideal customer profile (ICP)
- Scrapes company pages for contact details
- Scores each lead 1-10 against the ICP
- Drafts personalized cold emails for high-scoring leads
- Exports results to CSV

## Tech Stack
LangChain, LangGraph, Groq (Llama 3.1), Tavily, BeautifulSoup, Pandas

## How to run
1. Add API keys to `.env`
2. Run `python pipeline.py`
3. Enter your ICP criteria when prompted
4. Find results in `leads_output.csv`
