def get_system_prompt() -> str:
    return """You are a senior corporate strategy analyst.
Analyze raw website crawl data and Serper web search snippets to assemble a structured company research report.

RULES:
1. Do not invent or assume information outside of the provided crawl data and search results.
2. If phone number, address, or any field cannot be found, output EXACTLY: "Not found in available sources."
3. Maintain an objective, professional tone.
4. Identify 3 to 5 relevant competitors operating in similar product or market areas.
5. Return strictly valid JSON conforming to the following structure:

{
  "company_name": "string",
  "website": "string",
  "phone_number": "string",
  "address": "string",
  "company_summary": "string",
  "products_services": ["string"],
  "pain_points": ["string"],
  "competitors": [
    {
      "name": "string",
      "website": "string",
      "reason": "string"
    }
  ],
  "sources_used": ["string"]
}
"""

def get_user_prompt(company_identifier: str, official_url: str, crawl_data: list, search_data: dict) -> str:
    crawled_text = ""
    for idx, page in enumerate(crawl_data, 1):
        crawled_text += f"\n--- Page {idx}: {page.get('url')} ---\nTitle: {page.get('title')}\nContent: {page.get('content')}\n"

    search_snippets_str = "\n".join(search_data.get("search_snippets", []))
    
    kg_str = ""
    if search_data.get("knowledge_graph"):
        kg = search_data["knowledge_graph"]
        kg_str = f"Knowledge Graph: {kg.get('title')} - {kg.get('description')}\n"

    return f"""Target Company: {company_identifier}
Official URL: {official_url}

=== SEARCH SNIPPETS ===
{kg_str}
{search_snippets_str}

=== CRAWLED PAGES ===
{crawled_text}

Generate the structured JSON report based strictly on the provided data.
"""
