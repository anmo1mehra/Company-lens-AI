import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set
from src.utils import normalize_url, get_domain, clean_text

PRIORITY_KEYWORDS = [
    "home", "about", "company", "products", "services", 
    "solutions", "pricing", "contact", "customers", "industries"
]

IGNORE_KEYWORDS = [
    "login", "signup", "signin", "cart", "checkout", 
    "privacy", "terms", "careers", "blog", "page", 
    ".pdf", ".jpg", ".png", ".svg", "#", "javascript:"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

class CompanyCrawler:
    def __init__(self, start_url: str, max_pages: int = 10):
        self.start_url = normalize_url(start_url)
        self.target_domain = get_domain(self.start_url)
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.crawled_pages: List[Dict[str, str]] = []

    def _should_ignore(self, url: str) -> bool:
        url_lower = url.lower()
        if get_domain(url) != self.target_domain:
            return True
            
        parsed = urlparse(url_lower)
        path_query = parsed.path + "?" + parsed.query
        return any(kw in path_query or kw in url_lower for kw in IGNORE_KEYWORDS)

    def _score_url(self, url: str) -> int:
        score = sum(5 for kw in PRIORITY_KEYWORDS if kw in url.lower())
        if url.rstrip("/").lower() in [self.start_url.rstrip("/").lower(), f"https://{self.target_domain}"]:
            score += 10
        return score

    def _clean_html_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe", "button", "form"]):
            tag.decompose()
            
        blocks = []
        for elem in soup.find_all(["h1", "h2", "h3", "p", "li", "article"]):
            txt = elem.get_text(separator=" ", strip=True)
            if len(txt) > 20 and txt not in blocks:
                blocks.append(txt)
                
        return clean_text(" ".join(blocks))

    def crawl(self) -> List[Dict[str, str]]:
        queue = [(self._score_url(self.start_url), self.start_url)]
        
        while queue and len(self.crawled_pages) < self.max_pages:
            queue.sort(key=lambda x: x[0], reverse=True)
            _, current_url = queue.pop(0)
            
            norm_url = normalize_url(current_url).split("#")[0].rstrip("/")
            if norm_url in self.visited_urls:
                continue
            self.visited_urls.add(norm_url)

            try:
                res = requests.get(current_url, headers=HEADERS, timeout=7, allow_redirects=True)
                if res.status_code != 200 or "text/html" not in res.headers.get("Content-Type", "").lower():
                    continue

                html_text = res.text
                page_text = self._clean_html_text(html_text)

                if page_text and len(page_text) > 40:
                    soup = BeautifulSoup(html_text, "html.parser")
                    title = soup.title.string.strip() if soup.title and soup.title.string else current_url
                    self.crawled_pages.append({
                        "url": current_url,
                        "title": title,
                        "content": page_text[:2500]
                    })

                if len(self.crawled_pages) < self.max_pages:
                    soup = BeautifulSoup(html_text, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"].strip()
                        abs_url = urljoin(current_url, href)
                        clean_abs = normalize_url(abs_url).split("#")[0].rstrip("/")
                        
                        if clean_abs not in self.visited_urls and not self._should_ignore(clean_abs):
                            queue.append((self._score_url(clean_abs), clean_abs))

            except Exception:
                continue
                
        return self.crawled_pages
