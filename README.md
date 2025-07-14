# FetchSERP Python SDK

![PyPI](https://img.shields.io/pypi/v/fetchserp?color=blue)
![License](https://img.shields.io/badge/license-GPL%20v3-brightgreen)

A lightweight, dependency-free (except for [`requests`](https://pypi.org/project/requests/)) Python wrapper around the [FetchSERP](https://fetchserp.com) API.

With a single class (`FetchSERPClient`) you can:

* Retrieve live **search-engine result pages (SERPs)** in multiple formats (raw, HTML, JS-rendered, text).
* Analyse keyword & domain performance (search volume, ranking, Moz metrics, etc.).
* Scrape web pages (static or headless/JS, with or without proxy).
* Run on-page **SEO** / **AI** analyses.
* Inspect backlinks, emails, DNS, WHOIS, SSL and technology stacks.

---
## Installation

```bash
python -m pip install fetchserp
```

> Only the `requests` package is installed; no heavy dependencies.

---
## Quick start

```python
from fetchserp import FetchSERPClient

API_KEY = "YOUR_SECRET_API_KEY"

with FetchSERPClient(API_KEY) as fs:
    serp = fs.get_serp(query="python asyncio", pages_number=2)
    print(serp["data"]["results_count"], "results fetched")
```

The client raises `fetchserp.client.FetchSERPError` on any non-2xx response for easy error-handling.

---
## Authentication
All endpoints require a **Bearer token**. Pass your key when constructing the client:

```python
fs = FetchSERPClient("BEARER_TOKEN")
```

The SDK automatically adds `Authorization: Bearer <token>` to every request.

---
## Endpoints & SDK mapping

| SDK Method | HTTP | Path | Description |
|------------|------|------|-------------|
| `get_backlinks` | GET | `/api/v1/backlinks` | Backlinks for a domain |
| `get_domain_emails` | GET | `/api/v1/domain_emails` | Emails discovered on a domain |
| `get_domain_info` | GET | `/api/v1/domain_infos` | DNS, WHOIS, SSL & stack |
| `get_keywords_search_volume` | GET | `/api/v1/keywords_search_volume` | Google Ads search volume |
| `get_keywords_suggestions` | GET | `/api/v1/keywords_suggestions` | Keyword ideas by URL or seed list |
| `generate_long_tail_keywords` | GET | `/api/v1/long_tail_keywords_generator` | Long-tail keyword generator |
| `get_moz_domain_analysis` | GET | `/api/v1/moz` | Moz domain authority metrics |
| `check_page_indexation` | GET | `/api/v1/page_indexation` | Checks if a URL is indexed for a keyword |
| `get_domain_ranking` | GET | `/api/v1/ranking` | Ranking position of a domain for a keyword |
| `scrape_page` | GET | `/api/v1/scrape` | Static scrape (no JS) |
| `scrape_domain` | GET | `/api/v1/scrape_domain` | Crawl multiple pages of a domain |
| `scrape_page_js` | POST | `/api/v1/scrape_js` | Run custom JS & scrape |
| `scrape_page_js_with_proxy` | POST | `/api/v1/scrape_js_with_proxy` | JS scrape using residential proxy |
| `get_serp` | GET | `/api/v1/serp` | SERP (static) |
| `get_serp_html` | GET | `/api/v1/serp_html` | SERP with full HTML |
| `start_serp_js_job` | GET | `/api/v1/serp_js` | Launch JS-rendered SERP job (returns UUID) |
| `get_serp_js_result` | GET | `/api/v1/serp_js/{uuid}` | Poll job result |
| `get_serp_ai_mode` | GET | `/api/v1/serp_ai_mode` | SERP with AI Overview & AI Mode (fast, <30s) |
| `get_serp_text` | GET | `/api/v1/serp_text` | SERP + extracted text |
| `get_user` | GET | `/api/v1/user` | Current user info + credit balance |
| `get_webpage_ai_analysis` | GET | `/api/v1/webpage_ai_analysis` | Custom AI analysis of any webpage |
| `get_playwright_mcp` | GET | `/api/v1/playwright_mcp` | GPT-4.1 browser automation via Playwright MCP |
| `get_webpage_seo_analysis` | GET | `/api/v1/webpage_seo_analysis` | Full on-page SEO audit |

---
## Examples

### 1. Long-tail keyword ideas
```python
ideas = fs.generate_long_tail_keywords(keyword="electric cars", count=25)
```

### 2. JS-rendered SERP with AI overview
```python
job = fs.start_serp_js_job(query="best coffee makers", country="us")
result = fs.get_serp_js_result(uuid=job["data"]["uuid"])
print(result["data"]["results"][0]["ai_overview"]["content"])
```

### 3. Fast AI Overview & AI Mode (single call)
```python
result = fs.get_serp_ai_mode(query="how to learn python programming")
print(result["data"]["results"][0]["ai_overview"]["content"])
print(result["data"]["results"][0]["ai_mode_response"]["content"])
```

### 4. Scrape a page with custom JavaScript
```python
payload = {
    "url": "https://fetchserp.com",
    "js_script": "return { title: document.title, h1: document.querySelector('h1')?.textContent };"
}
result = fs.scrape_webpage_js(**payload)
```

### 5. Automate browser tasks with AI
```python
result = fs.get_playwright_mcp(prompt="Navigate to github.com and search for 'python selenium'")
print(result["data"]["response"])
```

### 6. Comprehensive SEO audit
```python
result = fs.get_webpage_seo_analysis(url="https://fetchserp.com")
print(result["data"]["summary"])
```

---
## Contributing
Pull requests are welcome! Please open an issue first to discuss major changes.

---
## License

GPL-3.0-or-later. See the [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) file for full text. 