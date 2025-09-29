import re
import json
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict, Set, List, Tuple, Optional
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup


@dataclass
class PageInfo:
    url: str
    title: Optional[str]
    status: Optional[int]
    depth: int
    discovered_from: List[str]
    out_links: List[str]


class Bot:
    """
    Site Mapper bot.

    Given a start URL, it crawls up to max_depth, prints:
    - a list of discovered URLs (grouped by depth)
    - a Mermaid diagram of the site graph

    It also attempts to find additional routes via robots.txt and sitemap.xml ("unexposed" routes),
    and includes them in the printed summary (not necessarily crawled if beyond depth).
    """

    name = "site_mapper"
    description = "Crawls a site map from a start URL and prints URL list + Mermaid diagram"
    author = "Scraper Kit"
    version = "0.1.0"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        })
        self.timeout = 15
        self.max_pages = 200  # safety cap

    def run(self, start_url: str, max_depth: int = 2, same_domain_only: bool = True) -> Dict[str, any]:
        if not start_url:
            print("Usage: python app.py run site_mapper --params <start_url> [max_depth] [same_domain_only]")
            return {"status": "error", "error": "missing_start_url"}

        start_url = self._canonicalize(start_url)
        start_host = urlparse(start_url).netloc

        robots_info = self._fetch_robots(start_url)
        sitemap_urls = self._discover_sitemaps(start_url, robots_info)
        sitemap_routes = self._fetch_sitemap_routes(sitemap_urls)

        visited: Set[str] = set()
        pages: Dict[str, PageInfo] = {}
        edges: List[Tuple[str, str]] = []  # (from, to)
        by_depth: Dict[int, List[str]] = defaultdict(list)

        q: deque[Tuple[str, int, Optional[str]]] = deque()
        q.append((start_url, 0, None))

        while q and len(visited) < self.max_pages:
            url, depth, parent = q.popleft()
            url = self._canonicalize(url)
            if url in visited:
                continue
            if same_domain_only and urlparse(url).netloc != start_host:
                continue
            visited.add(url)

            status, title, links = self._fetch_and_parse(url)
            pages[url] = PageInfo(url=url, title=title, status=status, depth=depth, discovered_from=[parent] if parent else [], out_links=links)
            by_depth[depth].append(url)
            if parent:
                edges.append((parent, url))

            if depth < max_depth:
                for l in links:
                    l = self._canonicalize(urljoin(url, l))
                    if not self._is_http(l):
                        continue
                    if same_domain_only and urlparse(l).netloc != start_host:
                        continue
                    if l not in visited:
                        q.append((l, depth + 1, url))

        # Prepare unexposed routes (from sitemap that weren't visited)
        unexposed = [u for u in sitemap_routes if u not in visited and (not same_domain_only or urlparse(u).netloc == start_host)]

        # Print summary list
        print("\nSite Map Summary")
        print("=" * 40)
        print(f"Start: {start_url}")
        print(f"Max depth: {max_depth}")
        print(f"Same domain only: {same_domain_only}")
        print(f"Pages crawled: {len(visited)}")
        print()
        for d in sorted(by_depth.keys()):
            print(f"Depth {d}:")
            for u in sorted(by_depth[d]):
                info = pages.get(u)
                title = f" — {info.title}" if info and info.title else ""
                status = f" [{info.status}]" if info and info.status else ""
                print(f"  - {u}{status}{title}")
            print("-" * 40)

        if unexposed:
            print("Potential unexposed routes (from sitemap):")
            for u in unexposed[:200]:  # cap output
                print(f"  - {u}")
            print("-" * 40)

        # Print Mermaid diagram
        print("Mermaid diagram:")
        print("```mermaid")
        print("graph TD")
        printed_nodes: Set[str] = set()
        def node_id(u: str) -> str:
            # Simple safe id
            return re.sub(r"[^a-zA-Z0-9]", "_", u)[:60]
        for frm, to in edges:
            nid_from = node_id(frm)
            nid_to = node_id(to)
            if frm not in printed_nodes:
                print(f"  {nid_from}[\"{frm}\"]")
                printed_nodes.add(frm)
            if to not in printed_nodes:
                print(f"  {nid_to}[\"{to}\"]")
                printed_nodes.add(to)
            print(f"  {nid_from} --> {nid_to}")
        if not edges:
            # Isolated single page
            nid = node_id(start_url)
            print(f"  {nid}[\"{start_url}\"]")
        print("```")

        return {
            "status": "success",
            "start": start_url,
            "pages": len(visited),
            "edges": len(edges),
            "unexposed_routes": len(unexposed),
        }

    # -----------------------------
    # Helpers
    # -----------------------------
    def _canonicalize(self, url: str) -> str:
        if not url:
            return url
        # remove fragments, strip spaces
        url, _ = urldefrag(url.strip())
        # normalize scheme-less URLs
        if url.startswith("//"):
            url = "https:" + url
        return url

    def _is_http(self, url: str) -> bool:
        scheme = urlparse(url).scheme.lower()
        return scheme in {"http", "https"}

    def _fetch_and_parse(self, url: str) -> Tuple[Optional[int], Optional[str], List[str]]:
        try:
            r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            status = r.status_code
            ctype = r.headers.get("Content-Type", "").lower()
            title = None
            links: List[str] = []
            if "text/html" in ctype or r.text.strip().startswith("<"):
                soup = BeautifulSoup(r.text, "html.parser")
                t = soup.find("title")
                title = t.get_text(strip=True) if t else None
                for a in soup.find_all("a", href=True):
                    href = a.get("href")
                    if href:
                        links.append(href)
                # Also parse meta refresh redirects
                for meta in soup.find_all("meta", attrs={"http-equiv": re.compile("refresh", re.I)}):
                    content = meta.get("content") or ""
                    m = re.search(r"url=([^;]+)", content, flags=re.I)
                    if m:
                        links.append(m.group(1).strip())
            return status, title, links
        except Exception:
            return None, None, []

    def _fetch_robots(self, start_url: str) -> str:
        p = urlparse(start_url)
        robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
        try:
            r = self.session.get(robots_url, timeout=self.timeout)
            if r.status_code < 400:
                return r.text
        except Exception:
            pass
        return ""

    def _discover_sitemaps(self, start_url: str, robots_txt: str) -> List[str]:
        found: List[str] = []
        for line in robots_txt.splitlines():
            if line.lower().startswith("sitemap:"):
                found.append(line.split(":", 1)[1].strip())
        if not found:
            p = urlparse(start_url)
            found.append(f"{p.scheme}://{p.netloc}/sitemap.xml")
        # dedupe
        seen = set()
        res = []
        for u in found:
            u = self._canonicalize(u)
            if u not in seen:
                seen.add(u)
                res.append(u)
        return res

    def _fetch_sitemap_routes(self, sitemap_urls: List[str]) -> List[str]:
        routes: List[str] = []
        for sm in sitemap_urls:
            try:
                r = self.session.get(sm, timeout=self.timeout)
                if r.status_code >= 400:
                    continue
                text = r.text
                # very simple XML parsing via regex to avoid adding dependencies
                for loc in re.findall(r"<loc>(.*?)</loc>", text, flags=re.I):
                    routes.append(self._canonicalize(loc.strip()))
                # handle index sitemaps that list other sitemaps
                for child in re.findall(r"<sitemap>.*?<loc>(.*?)</loc>.*?</sitemap>", text, flags=re.I | re.S):
                    routes.extend(self._fetch_sitemap_routes([self._canonicalize(child.strip())]))
            except Exception:
                continue
        # dedupe
        dedup = []
        seen = set()
        for u in routes:
            if u not in seen:
                seen.add(u)
                dedup.append(u)
        return dedup
