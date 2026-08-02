import re
from urllib.parse import urlparse, urlunparse

def is_url(input_str: str) -> bool:
    cleaned = input_str.strip()
    if re.match(r"^https?://", cleaned, re.IGNORECASE):
        return True
    
    domain_pattern = r"^(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(/.*)?$"
    return bool(re.match(domain_pattern, cleaned))

def normalize_url(url: str) -> str:
    cleaned = url.strip()
    if not cleaned.startswith(("http://", "https://")):
        cleaned = "https://" + cleaned
    
    parsed = urlparse(cleaned)
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.params, parsed.query, parsed.fragment))

def get_domain(url: str) -> str:
    parsed = urlparse(normalize_url(url))
    netloc = parsed.netloc.split(":")[0].lower()
    if netloc.startswith("www."):
        return netloc[4:]
    return netloc

def clean_text(text: str) -> str:
    if not text:
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return re.sub(r"\s+", " ", " ".join(lines)).strip()

def sanitize_filename(name: str) -> str:
    sanitized = re.sub(r"[^\w\-_]", "_", name.strip())
    return re.sub(r"_+", "_", sanitized).strip("_")
