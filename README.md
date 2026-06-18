# Lead Generation Agent

An AI multi-agent pipeline that automates lead research and outreach for sales teams. Given an Ideal Customer Profile (ICP), the system autonomously searches the web, extracts company and contact information, scores lead relevance, and drafts personalized cold emails — all exported to a CSV file.

---

## Project Overview and Objectives

Finding qualified leads is one of the biggest bottlenecks for sales teams. This project automates the entire lead research process by:

- Taking a structured Ideal Customer Profile (ICP) as input
- Searching the web for matching companies and decision-makers
- Scraping company pages for deeper contact details
- Scoring each lead against the ICP on a 1-10 scale
- Drafting personalized cold emails for high-scoring leads (score ≥ 7)
- Exporting all results to a structured CSV file

The goal is to reduce manual research time and give sales teams a ready-to-use list of qualified leads with outreach emails already drafted.

---

## Architecture and Design

The system follows a **sequential multi-agent pipeline** with 4 steps:

The pipeline runs sequentially as each step feeds its output directly into the next via a shared `state` dictionary, so nothing gets lost between steps.

**Step 1 — Search Agent**
Takes the ICP and generates targeted search queries. Uses the Tavily API to run 3+ searches and return real company results with titles, URLs, and snippets. The agent decides what to search for and when it has enough results.

**Step 2 — Extractor Agent**
Takes the search results from Step 1, picks the most promising URLs, and scrapes each page using BeautifulSoup. Strips out all the noise (scripts, styles, navigation) and pulls out clean text to find company names, websites, and decision-maker details.

**Step 3 — Scorer Chain**
Takes the combined research from Steps 1 and 2 and scores each lead against the ICP on a scale of 1-10. Uses a Pydantic model to force the LLM to return structured data and instead of a paragraph of text, you get back a clean object with specific fields like `company_name`, `relevance_score`, and `score_reason`.

**Step 4 — Email Chain**
Loops through the scored leads and writes a personalized cold email for any lead that scored 7 or above. Skips low-quality leads to save time and API calls.

**Output**
Everything gets compiled into a pandas DataFrame and saved to `leads_output.csv`.

---

## Features and Functionalities

- **ICP-based search** — accepts industry, company size, target title, and funding stage as input
- **Automated web search** — uses Tavily API to find real companies and decision-makers
- **Web scraping** — extracts clean text from company pages using BeautifulSoup
- **Lead scoring** — scores each lead 1-10 with a one-sentence justification
- **Email drafting** — generates personalized cold emails for high-scoring leads
- **CSV export** — outputs all leads with scores, reasons, and email drafts to `leads_output.csv`
- **Error handling** — gracefully skips failed leads without crashing the pipeline

---

## Technology Stack

| Tool | Purpose |
|------|---------|
| [LangChain](https://langchain.com) | Agent and chain orchestration |
| [LangGraph](https://langchain-ai.github.io/langgraph/) | ReAct agent execution runtime |
| [Groq + Llama 3.1 8B](https://console.groq.com) | LLM (free, fast inference) |
| [Tavily](https://tavily.com) | Real-time web search API |
| [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) | HTML scraping and parsing |
| [Pydantic](https://docs.pydantic.dev) | Structured data validation (Lead model) |
| [Pandas](https://pandas.pydata.org) | CSV export and data handling |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable management |

---

## Project Structure

lead_gen_agent/
│
├── tools.py          # the two tools agents can use — web search and page scraping
├── agents.py         # LLM connection, Lead data model, search/extractor agents, scorer and email chains
├── pipeline.py       # runs all 4 steps in order, handles state passing, exports CSV
├── requirements.txt  # all dependencies needed to run the project
├── .env              # API keys — never committed to GitHub
└── leads_output.csv  # generated output file, overwritten on each run



## Setup and Installation

### Prerequisites
- Python 3.10 or higher
- A Groq API key (free at [console.groq.com](https://console.groq.com))
- A Tavily API key (free at [app.tavily.com](https://app.tavily.com))

### Steps

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/lead_gen_agent.git
cd lead_gen_agent
```

**2. Create and activate a virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows


**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## Configuration

**4. Create a `.env` file in the project root:**
```
TAVILY_API_KEY=your_tavily_key_here
GROQ_API_KEY=your_groq_key_here
```

>  Never commit your `.env` file to GitHub. 

---

##  Usage

**Run the pipeline:**
```bash
python pipeline.py
```

You will be prompted to enter your ICP criteria:
```
Industry (e.g. healthcare technology): 
Company size (e.g. 50-500 employees): 
Target title (e.g. VP of Sales): 
Funding stage (e.g. Series A-C): 
```

The pipeline will run all 4 steps and save results to `leads_output.csv`.

---

## Usage Example

**Input ICP:**
```
Industry: healthcare technology
Company size: 50-500 employees
Target title: VP of Sales
Funding stage: Series A-C
```

**Output CSV columns:**

| Company | Website | Contact Name | Contact Title | Score | Score Reason | Email Draft |
|---------|---------|--------------|---------------|-------|--------------|-------------|
| Lucem Health | lucemhealth.com | Kyle | VP of Sales | 8 | Matches ICP on industry and funding stage | Hi Kyle, I came across Lucem Health... |
| Solace Health | solacehealth.com | CEO | CEO | 8 | Matches ICP on industry and company size | Hi [CEO's Name]... |

---

## API Details

### Tools (`tools.py`)

**`search_leads(query: str) -> str`**
- Searches the web using Tavily API
- Returns titles, URLs, and snippets of matching results
- `max_results=5` per query

**`scrape_lead_page(url: str) -> str`**
- Fetches and parses a webpage using requests + BeautifulSoup
- Removes scripts, styles, headers, footers
- Returns first 3000 characters of clean text
- Includes timeout and error handling

### Lead Model (`agents.py`)

```python
class Lead(BaseModel):
    company_name: str
    website: str
    contact_name: str
    contact_title: str
    relevance_score: int  # 1-10
    score_reason: str
    email_draft: str
```

---

## Assumptions, Limitations, and Known Issues

**Assumptions:**
- Target companies are findable via public web search
- Decision-maker contact details may not always be available on public pages
- Groq free tier is sufficient for development and testing

**Limitations:**
- **Token limits:** Groq free tier has a 100,000 token/day limit. Running multiple times in one day may hit this limit
- **Lead deduplication:** The scorer chain may occasionally return the same company for multiple leads — this is a known LLM behavior with limited context
- **Contact accuracy:** Contact names and titles are extracted from public web data and may not always be accurate
- **LinkedIn scraping:** LinkedIn is not scraped directly due to ToS restrictions. Public search snippets are used instead

**Known Issues:**
- File names with spaces cause virtual environment path issues on Mac

---

##  Future Enhancements

- **Streamlit UI** — add a visual web interface for non-technical users
- **LinkedIn integration** — use official LinkedIn API for more accurate contact data
- **Deduplication** — add logic to ensure unique companies across all 5 leads
- **Email personalization** — use scraped content for deeper email personalization
- **CRM integration** — push leads directly to Salesforce or HubSpot
- **Batch processing** — run multiple ICPs in parallel
- **Lead enrichment** — add company size, revenue, and tech stack data via APIs like Clearbit
