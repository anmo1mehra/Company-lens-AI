import json
import re
import requests
from typing import Dict, Any
from src.prompts import get_system_prompt, get_user_prompt

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODELS = [
    "openai/gpt-4o-mini",
    "google/gemini-2.0-flash-001",
    "anthropic/claude-3.5-sonnet",
    "deepseek/deepseek-r1",
    "meta-llama/llama-3.3-70b-instruct"
]

class OpenRouterClient:
    def __init__(self, api_key: str):
        key = api_key.strip() if api_key else ""
        if key and not key.startswith("sk-or-"):
            key = f"sk-or-{key}"
        self.api_key = key

    def generate_company_research(
        self,
        company_identifier: str,
        official_url: str,
        crawl_data: list,
        search_data: dict,
        model: str = "openai/gpt-4o-mini"
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OpenRouter API key missing.")

        system_prompt = get_system_prompt()
        user_prompt = get_user_prompt(company_identifier, official_url, crawl_data, search_data)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://companylens.ai",
            "X-Title": "CompanyLens AI",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 3000
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=45)
        if response.status_code != 200:
            raise RuntimeError(f"OpenRouter API returned status {response.status_code}: {response.text}")

        res_json = response.json()
        raw_content = res_json["choices"][0]["message"]["content"].strip()
        
        if raw_content.startswith("```"):
            raw_content = re.sub(r"^```(?:json)?\n?", "", raw_content)
            raw_content = re.sub(r"\n?```$", "", raw_content).strip()

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
            else:
                raise ValueError("Could not parse JSON from model response.")

        return {
            "company_name": parsed.get("company_name", company_identifier),
            "website": parsed.get("website", official_url),
            "phone_number": parsed.get("phone_number", "Not found in available sources."),
            "address": parsed.get("address", "Not found in available sources."),
            "company_summary": parsed.get("company_summary", "Not found in available sources."),
            "products_services": parsed.get("products_services", []),
            "pain_points": parsed.get("pain_points", []),
            "competitors": parsed.get("competitors", []),
            "sources_used": parsed.get("sources_used", [official_url])
        }
