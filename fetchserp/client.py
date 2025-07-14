import requests
from typing import Any, Dict, List, Optional, Union


class FetchSERPError(Exception):
    """Raised when the FetchSERP API returns an error or an unexpected response."""


class FetchSERPClient:
    """Light-weight Python SDK for the FetchSERP API.

    Only the requests dependency is required. All public methods mirror an API
    endpoint described in the official documentation. Optional parameters can
    be omitted, falling back to the server defaults documented by FetchSERP.
    """

    def __init__(self, api_key: str, base_url: str = "https://www.fetchserp.com") -> None:
        if not api_key:
            raise ValueError("An API key must be provided.")

        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "fetchserp-python-sdk/0.3.0",
                "Accept": "application/json",
            }
        )

    # ---------------------------------------------------------------------
    # Low-level HTTP helpers
    # ---------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Union[int, float] = 30,
    ) -> Any:
        """Internal request wrapper with basic error handling."""

        url = f"{self.base_url}{path}"
        response = self.session.request(method.upper(), url, params=params, json=json, timeout=timeout)

        # Raise for HTTP errors first to catch 4xx/5xx quickly
        if response.status_code >= 400:
            raise FetchSERPError(f"{response.status_code}: {response.text}")

        # Try to decode JSON – some endpoints may return plain text
        try:
            return response.json()
        except ValueError:
            return response.text

    # ---------------------------------------------------------------------
    # Convenience helpers
    # ---------------------------------------------------------------------

    def _clean_params(self, params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not params:
            return None
        return {k: v for k, v in params.items() if v is not None}

    def _get(self, path: str, **params: Any) -> Any:
        return self._request("GET", path, params=self._clean_params(params))

    def _post(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self._request("POST", path, params=self._clean_params(params), json=json)

    # ---------------------------------------------------------------------
    # API Endpoints – Backlinks & Domain data
    # ---------------------------------------------------------------------

    def get_backlinks(
        self,
        *,
        domain: str,
        search_engine: str = "google",
        country: str = "us",
        pages_number: int = 15,
    ) -> Any:
        """Get backlinks for a domain."""
        return self._get(
            "/api/v1/backlinks",
            domain=domain,
            search_engine=search_engine,
            country=country,
            pages_number=pages_number,
        )

    def get_domain_emails(
        self,
        *,
        domain: str,
        search_engine: str = "google",
        country: str = "us",
        pages_number: int = 1,
    ) -> Any:
        """Retrieve emails found for the supplied domain."""
        return self._get(
            "/api/v1/domain_emails",
            domain=domain,
            search_engine=search_engine,
            country=country,
            pages_number=pages_number,
        )

    def get_domain_info(self, *, domain: str) -> Any:
        """Fetch DNS, WHOIS, SSL & stack information for a domain."""
        return self._get("/api/v1/domain_infos", domain=domain)

    # ---------------------------------------------------------------------
    # Keywords utilities
    # ---------------------------------------------------------------------

    def get_keywords_search_volume(self, *, keywords: List[str], country: str = "us") -> Any:
        """Obtain monthly search volume data for one or more keywords."""
        return self._get("/api/v1/keywords_search_volume", keywords=keywords, country=country)

    def get_keywords_suggestions(
        self,
        *,
        url: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        country: str = "us",
    ) -> Any:
        """Generate keyword suggestions from either a page URL or a seed list of keywords."""
        if not url and not keywords:
            raise ValueError("Either 'url' or 'keywords' must be provided.")
        return self._get("/api/v1/keywords_suggestions", url=url, keywords=keywords, country=country)

    def generate_long_tail_keywords(
        self,
        *,
        keyword: str,
        search_intent: str = "informational",
        count: int = 10,
    ) -> Any:
        """Produce long-tail keyword ideas for a given seed keyword."""
        return self._get(
            "/api/v1/long_tail_keywords_generator",
            keyword=keyword,
            search_intent=search_intent,
            count=count,
        )

    def get_moz_domain_analysis(self, *, domain: str) -> Any:
        """Retrieve Moz domain authority metrics."""
        return self._get("/api/v1/moz", domain=domain)

    # ---------------------------------------------------------------------
    # Indexation & Ranking
    # ---------------------------------------------------------------------

    def check_page_indexation(self, *, domain: str, keyword: str) -> Any:
        """Check if a page is indexed in SERP for a keyword."""
        return self._get("/api/v1/page_indexation", domain=domain, keyword=keyword)

    def get_domain_ranking(
        self,
        *,
        keyword: str,
        domain: str,
        search_engine: str = "google",
        country: str = "us",
        pages_number: int = 10,
    ) -> Any:
        """Retrieve domain ranking for a keyword on a given search engine and locale."""
        return self._get(
            "/api/v1/ranking",
            keyword=keyword,
            domain=domain,
            search_engine=search_engine,
            country=country,
            pages_number=pages_number,
        )

    # ---------------------------------------------------------------------
    # Scraping endpoints
    # ---------------------------------------------------------------------

    def scrape_page(self, *, url: str) -> Any:
        """Scrape a web page without executing JavaScript."""
        return self._get("/api/v1/scrape", url=url)

    def scrape_domain(self, *, domain: str, max_pages: int = 10) -> Any:
        """Scrape multiple pages from a domain (static scrape)."""
        return self._get("/api/v1/scrape_domain", domain=domain, max_pages=max_pages)

    def scrape_page_js(self, *, url: str, js_script: Optional[str] = None) -> Any:
        """Scrape a web page after executing custom JavaScript."""
        return self._post("/api/v1/scrape_js", params={"url": url, "js_script": js_script})

    def scrape_page_js_with_proxy(
        self,
        *,
        url: str,
        country: str,
        js_script: Optional[str] = None,
    ) -> Any:
        """Scrape a web page with JavaScript execution using a residential proxy in the selected country."""
        params: Dict[str, Any] = {"url": url, "country": country}
        if js_script is not None:
            params["js_script"] = js_script
        return self._post("/api/v1/scrape_js_with_proxy", params=params)

    # ---------------------------------------------------------------------
    # SERP endpoints
    # ---------------------------------------------------------------------

    def get_serp(
        self,
        *,
        query: str,
        search_engine: str = "google",
        country: str = "us",
        pages_number: int = 1,
    ) -> Any:
        """Retrieve search engine results (static, no JS)."""
        return self._get(
            "/api/v1/serp",
            query=query,
            search_engine=search_engine,
            country=country,
            pages_number=pages_number,
        )

    def get_serp_html(
        self,
        *,
        query: str,
        search_engine: str = "google",
        country: str = "us",
        pages_number: int = 1,
    ) -> Any:
        """Retrieve SERP results including full HTML of each page."""
        return self._get(
            "/api/v1/serp_html",
            query=query,
            search_engine=search_engine,
            country=country,
            pages_number=pages_number,
        )

    def start_serp_js_job(
        self,
        *,
        query: str,
        country: str = "us",
        pages_number: int = 1,
    ) -> Any:
        """Launch an asynchronous SERP job with JS rendering & AI overview (step 1)."""
        return self._get("/api/v1/serp_js", query=query, country=country, pages_number=pages_number)

    def get_serp_js_result(self, *, uuid: str) -> Any:
        """Poll the SERP JS job to obtain the final results (step 2)."""
        return self._get(f"/api/v1/serp_js/{uuid}")

    def get_serp_text(
        self,
        *,
        query: str,
        search_engine: str = "google",
        country: str = "us",
        pages_number: int = 1,
    ) -> Any:
        """Retrieve SERP results along with extracted visible text from each page."""
        return self._get(
            "/api/v1/serp_text",
            query=query,
            search_engine=search_engine,
            country=country,
            pages_number=pages_number,
        )

    def get_serp_ai_mode(self, *, query: str) -> Any:
        """Get SERP with AI Overview and AI Mode response. Returns AI overview and AI mode response for the query. Less reliable than the 2-step process but returns results in under 30 seconds."""
        return self._get("/api/v1/serp_ai_mode", query=query)

    # ---------------------------------------------------------------------
    # User & AI / SEO analysis
    # ---------------------------------------------------------------------

    def get_user(self) -> Any:
        """Fetch information about the current API user and remaining credits."""
        return self._get("/api/v1/user")

    def get_webpage_ai_analysis(self, *, url: str, prompt: str) -> Any:
        """Analyze a webpage using AI with a custom prompt."""
        return self._get("/api/v1/webpage_ai_analysis", url=url, prompt=prompt)

    def get_playwright_mcp(self, *, prompt: str) -> Any:
        """Use GPT-4.1 to remote control a browser via a Playwright MCP server."""
        return self._get("/api/v1/playwright_mcp", prompt=prompt)

    def get_webpage_seo_analysis(self, *, url: str) -> Any:
        """Run a full on-page SEO audit for a given URL."""
        return self._get("/api/v1/web_page_seo_analysis", url=url)

    # ---------------------------------------------------------------------
    # Misc helpers
    # ---------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying requests session (optional)."""
        self.session.close()

    def __enter__(self):  # noqa: D401 – context manager
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: D401
        self.close() 