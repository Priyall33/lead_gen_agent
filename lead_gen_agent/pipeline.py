from agents import ( 
    build_search_agent,
    build_extractor_agent,
    scorer_chain,
    email_chain
)
import pandas as pd 

def run_lead_gen_pipeline(icp: dict) -> dict:
    state = {}

    # Search Agent
    print("\n" + "="*50)
    print("step 1 - Search Agent finding leads... ")
    print("="*50)

    search_agent = build_search_agent()  # calls function from agents
    search_result = search_agent.invoke({  # runs agent with a message
        "messages": [("user", f"Find companies and decision makers matching this ICP: {icp}. Run 3+ searches.")]
    })
    state["search_results"] = search_result["messages"][-1].content  # takes agents final answer and extracts it
    print("\nSearch Results:\n", state["search_results"])


    # Extractor Agent
    print("\n" + "="*50)
    print("Step 2 — Extractor Agent pulling lead details...")
    print("="*50)

    extractor_agent = build_extractor_agent()
    extractor_result = extractor_agent.invoke({
        "messages": [("user", f"Scrape the best pages from these search results to get company and contact details:\n\n{state['search_results'][:1000]}")]
    })
    state["extracted_info"] = extractor_result["messages"][-1].content
    print("\nExtracted Info:\n", state["extracted_info"])


    # Scorer Chain
    print("\n" + "="*50)
    print("Step 3 — Scoring leads against ICP...")
    print("="*50)

    combined = f"Search:\n{state['search_results'][:500]}\n\nScraped:\n{state['extracted_info'][:500]}"  # combines the result of step 1/2 into one string
    leads = []

    for i in range(1, 6):  # 5 different score leads
        try:
            lead = scorer_chain.invoke({
                "icp": icp,
                "raw_lead_info": f"Extract lead #{i}, You MUST pick company number {i} specifically, do not repeat companies:\n\n{combined}"
            })
            leads.append(lead)  # adds each scored lead to list
            print(f"Lead {i}: {lead.company_name} — {lead.relevance_score}/10")
        except Exception as e:
            print(f"Could not score lead {i}: {e}")
            continue  # skips to next loop if error comes

    state["leads"] = leads

    # Email Chain
    print("\n" + "="*50)
    print("Step 4 — Drafting emails for high scoring leads...")
    print("="*50)

    for lead in state["leads"]:
        if int(lead.relevance_score) >= 7:  # writes email if scored more than 7
            lead.email_draft = email_chain.invoke({  # calls email chain from agents and passes in the lead's details
                "company_name": lead.company_name,
                "contact_name": lead.contact_name,
                "contact_title": lead.contact_title,
                "score_reason": lead.score_reason
            })
            print(f"Email drafted for {lead.company_name}")


    # Save to CSV
    rows = []
    for lead in state["leads"]:  # loops through leads and converts into objects
        rows.append({
            "Company": lead.company_name,
            "Website": lead.website,
            "Contact Name": lead.contact_name,
            "Contact Title": lead.contact_title,
            "Score": lead.relevance_score,
            "Score Reason": lead.score_reason,
            "Email Draft": getattr(lead, 'email_draft', None)
        })

    df = pd.DataFrame(rows)  # convert dict to pandas table
    df.to_csv("leads_output.csv", index=False)
    state["dataframe"] = df  # saves the dataframe into a state

    print("\nDone! leads_output.csv saved.")
    print(df[["Company", "Score"]].to_string())

    return state

 
if __name__ == "__main__": #This would onyl appear when running pipline.py directly 
    icp = {
        "industry": input("Industry (e.g. healthcare technology): "),
        "company_size": input("Company size (e.g. 50-500 employees): "),
        "target_title": input("Target title (e.g. VP of Sales): "),
        "funding_stage": input("Funding stage (e.g. Series A-C): ")
    }
    run_lead_gen_pipeline(icp)