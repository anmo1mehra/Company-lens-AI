import requests
from typing import Dict, Any, Optional
from src.utils import normalize_url

SERPER_API_URL = "https://google.serper.dev/search"

def call_serper_api(query: str, api_key: str, num: int = 10) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None
        
    headers = {
        "X-API-KEY": api_key.strip(),
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": num}
    
    try:
        res = requests.post(SERPER_API_URL, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def find_official_website(company_name: str, api_key: str) -> Optional[str]:
    query = f"{company_name} official website homepage"
    data = call_serper_api(query, api_key, num=5)
    
    if not data or "organic" not in data:
        return None
        
    skip_domains = ["wikipedia.org", "linkedin.com", "facebook.com", "twitter.com", "x.com", "crunchbase.com", "youtube.com"]
    
    for item in data["organic"]:
        link = item.get("link", "")
        if link and not any(skip in link.lower() for skip in skip_domains):
            return normalize_url(link)
                
    if data["organic"]:
        return normalize_url(data["organic"][0].get("link", ""))
        
    return None

def gather_serper_insights(company_identifier: str, official_url: str, api_key: str) -> Dict[str, Any]:
    insights = {
        "organic_results": [],
        "knowledge_graph": {},
        "competitor_leads": [],
        "search_snippets": []
    }
    
    if not api_key:
        return insights

    res1 = call_serper_api(f"{company_identifier} company overview products contact phone address headquarters", api_key, num=8)
    if res1:
        if "knowledgeGraph" in res1:
            insights["knowledge_graph"] = res1["knowledgeGraph"]
        for item in res1.get("organic", []):
            insights["search_snippets"].append(f"Title: {item.get('title')}\nURL: {item.get('link')}\nSnippet: {item.get('snippet')}")
            insights["organic_results"].append(item)

    res2 = call_serper_api(f"top competitors and alternatives to {company_identifier}", api_key, num=8)
    if res2:
        for item in res2.get("organic", []):
            insights["search_snippets"].append(f"Title: {item.get('title')}\nURL: {item.get('link')}\nSnippet: {item.get('snippet')}")
            insights["competitor_leads"].append(item)

    return insights
