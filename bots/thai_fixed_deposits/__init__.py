import re
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup


class Bot:
    """
    Thai Fixed Deposit scraper.

    Scrapes fixed/time-deposit interest rate tables from major Thai banks and outputs
    normalized data for easy comparison.
    """

    name = "thai_fixed_deposits"
    description = "Scrapes fixed deposit (time deposit) interest rates from major Thai banks in Thailand"
    author = "Scraper Kit"
    version = "0.1.0"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        self.timeout = 20
        self.output_dir = "data/thai_fixed_deposits"

        # Candidate URLs per bank (kept as a list to improve robustness if structures move)
        self.bank_sources: Dict[str, List[str]] = {
            "bangkok_bank": [
                # EN
                "https://www.bangkokbank.com/en/Personal/Saving-and-Investment/Savings/Time-Deposit/Interest-Rates",
                # TH
                "https://www.bangkokbank.com/th-TH/Personal/Saving-and-Investment/Savings/Time-Deposit/Interest-Rates",
            ],
            "kasikorn": [
                # KBank interest rate pages periodically move; try a few likely endpoints
                "https://www.kasikornbank.com/en/rate/Pages/depositRate.aspx",
                "https://www.kasikornbank.com/en/personal/saving-investment/Pages/interest-rates.aspx",
                "https://www.kasikornbank.com/th/personal/save/pages/interest-rate.aspx",
            ],
            "gh_bank": [
                # Government Housing Bank (GHB)
                "https://www.ghbank.co.th/en/interest-rate",
                "https://www.ghbank.co.th/en/deposit/interest-rate",
                "https://www.ghbank.co.th/interest-rate",
            ],
        }

    # -----------------------------
    # Public API
    # -----------------------------
    def run(self, *banks: str, delay_seconds: float = 0.8) -> Dict[str, Any]:
        """
        Run the scraper.

        :param banks: Optional list of bank keys to scrape. Defaults to all supported banks.
        :param delay_seconds: Delay between HTTP requests to be polite.
        :return: dict containing scrape results and output file path.
        """
        try:
            import os
            os.makedirs(self.output_dir, exist_ok=True)

            target_banks = list(banks) if banks else list(self.bank_sources.keys())

            results: Dict[str, Any] = {
                "scraped_at": datetime.utcnow().isoformat(),
                "banks": {},
                "errors": {},
            }

            for bank in target_banks:
                try:
                    data = self._scrape_bank(bank, delay_seconds=delay_seconds)
                    results["banks"][bank] = data
                except Exception as e:
                    results["errors"][bank] = str(e)
                time.sleep(delay_seconds)

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.output_dir}/fd_rates_{timestamp}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            print(f"Saved results to {output_file}")
            return {"status": "success", "output_file": output_file, "banks": list(results["banks"].keys()), "errors": results["errors"]}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Basic analysis: find the highest rate per common term across banks.
        Expects data in the format returned by `run()` file payload content (banks -> {offers:[...]})
        """
        if not data or "banks" not in data:
            return {"message": "No data to analyze"}

        # normalize and aggregate
        term_best: Dict[str, Dict[str, Any]] = {}
        for bank, payload in data.get("banks", {}).items():
            offers = (payload or {}).get("offers", [])
            for offer in offers:
                term = offer.get("term") or offer.get("tenor") or offer.get("period")
                rate = offer.get("rate")
                if term and isinstance(rate, (int, float)):
                    if term not in term_best or rate > term_best[term]["rate"]:
                        term_best[term] = {"bank": bank, "rate": rate, "name": offer.get("product")}

        return {"top_rates_by_term": term_best, "banks_analyzed": list(data.get("banks", {}).keys())}

    # -----------------------------
    # Internal helpers
    # -----------------------------
    def _scrape_bank(self, bank: str, delay_seconds: float = 0.8) -> Dict[str, Any]:
        if bank not in self.bank_sources:
            raise ValueError(f"Unsupported bank: {bank}")

        offers: List[Dict[str, Any]] = []
        tried_urls: List[str] = []
        for url in self.bank_sources[bank]:
            tried_urls.append(url)
            try:
                html = self._fetch(url)
                if not html:
                    continue
                soup = BeautifulSoup(html, "html.parser")

                # Try table-driven extraction first
                table_offers = self._extract_from_tables(soup)
                if table_offers:
                    offers.extend(table_offers)

                # Additionally, attempt a generic pattern search across lists/divs
                generic_offers = self._extract_generic_blocks(soup)
                for g in generic_offers:
                    if g not in offers:
                        offers.append(g)

                if offers:
                    break  # Found data on this URL
            except Exception:
                # Try next candidate URL
                continue
            finally:
                time.sleep(delay_seconds)

        # De-duplicate by (term, rate, product)
        dedup: Dict[str, Dict[str, Any]] = {}
        for o in offers:
            key = f"{o.get('term')}|{o.get('rate')}|{(o.get('product') or '').lower()}"
            dedup[key] = o

        return {
            "bank": bank,
            "scraped_at": datetime.utcnow().isoformat(),
            "tried_urls": tried_urls,
            "offers": list(dedup.values()),
        }

    def _fetch(self, url: str) -> Optional[str]:
        resp = self.session.get(url, timeout=self.timeout)
        if resp.status_code >= 400:
            return None
        return resp.text

    def _extract_from_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        offers: List[Dict[str, Any]] = []
        tables = soup.find_all("table")
        for table in tables:
            headers = [self._norm_text(th.get_text(" ")) for th in table.find_all(["th", "td"], recursive=True)][:10]
            header_blob = " ".join(headers)
            if not self._looks_like_rate_table(header_blob):
                # Skip unrelated tables
                continue

            for tr in table.find_all("tr"):
                cells = [self._norm_text(td.get_text(" ")) for td in tr.find_all(["td", "th"])]
                if len(cells) < 2:
                    continue
                # Try to find a term (e.g., 3 months, 6M, 12 เดือน) and a rate (e.g., 1.50%)
                term = self._extract_term(" ".join(cells))
                rate = self._extract_rate(" ".join(cells))

                if term and rate is not None:
                    product = None
                    # If there are more than 2 cells, first cell may be product name
                    if len(cells) >= 3:
                        product = cells[0]
                    offers.append({
                        "product": product,
                        "term": term,
                        "rate": rate,
                        "raw": cells,
                    })
        return offers

    def _extract_generic_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        offers: List[Dict[str, Any]] = []
        blocks = soup.find_all(["section", "div", "li", "article"])
        for b in blocks:
            text = self._norm_text(b.get_text(" "))
            if "%" not in text:
                continue
            rate = self._extract_rate(text)
            term = self._extract_term(text)
            if rate is not None and term:
                offers.append({"product": None, "term": term, "rate": rate, "raw": text[:180]})
        return offers

    def _looks_like_rate_table(self, text: str) -> bool:
        keywords = [
            "interest", "rate", "deposit", "time", "fixed",
            # Thai equivalents
            "ดอกเบี้ย", "อัตรา", "เงินฝาก", "ประจำ", "เดือน",
        ]
        t = text.lower()
        return any(k in t for k in keywords)

    def _extract_rate(self, text: str) -> Optional[float]:
        # Capture patterns like 1.50%, 2%, 0.85 %
        m = re.search(r"(\d{1,2}(?:\.\d{1,3})?)\s*%", text)
        if not m:
            return None
        try:
            return float(m.group(1))
        except ValueError:
            return None

    def _extract_term(self, text: str) -> Optional[str]:
        t = text.lower()
        # English months/years
        m = re.search(r"(\d{1,2})\s*(month|months|mo|m)\b", t)
        if m:
            return f"{int(m.group(1))}M"
        m = re.search(r"(\d{1,2})\s*(year|years|yr|y)\b", t)
        if m:
            return f"{int(m.group(1))}Y"
        # Thai: e.g., 3 เดือน, 12 เดือน, 1 ปี
        m = re.search(r"(\d{1,2})\s*เดือน", t)
        if m:
            return f"{int(m.group(1))}M"
        m = re.search(r"(\d{1,2})\s*ปี", t)
        if m:
            return f"{int(m.group(1))}Y"
        # Sometimes shown like 3M/6M/12M
        m = re.search(r"\b(\d{1,2})\s*[mM]\b", t)
        if m:
            return f"{int(m.group(1))}M"
        m = re.search(r"\b(\d{1,2})\s*[yY]\b", t)
        if m:
            return f"{int(m.group(1))}Y"
        return None

    @staticmethod
    def _norm_text(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "")).strip()
