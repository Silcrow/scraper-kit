import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class Bot:
    """
    Thai Fixed Deposit Report bot.

    Reads the latest scraped JSON from `data/thai_fixed_deposits/` (or a provided path)
    and prints a simple report to stdout: each bank and its offers with terms and rates.
    """

    name = "thai_fd_report"
    description = "Reads thai_fixed_deposits scraped results and prints a CLI report"
    author = "Scraper Kit"
    version = "0.1.0"

    def __init__(self):
        self.default_dir = Path("data/thai_fixed_deposits")

    def run(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        :param file_path: Optional path to a JSON file produced by `thai_fixed_deposits`.
                          If omitted, the latest file in `data/thai_fixed_deposits/` is used.
        """
        data = self._load_data(file_path)
        if not data:
            print("No data found to report.")
            return {"status": "error", "error": "no_data"}

        banks = data.get("banks", {})
        errors = data.get("errors", {})

        print("\nThai Fixed Deposit Offers Report")
        print("=" * 40)
        print(f"Scraped at: {data.get('scraped_at', 'unknown')}")
        print()

        total_offers = 0
        for bank_key, payload in banks.items():
            offers: List[Dict[str, Any]] = (payload or {}).get("offers", [])
            print(f"Bank: {bank_key}")
            if not offers:
                print("  (no offers found)")
                print("-" * 40)
                continue

            for offer in offers:
                product = offer.get("product") or "(product)"
                term = offer.get("term") or offer.get("tenor") or offer.get("period") or "?"
                rate = offer.get("rate")
                if isinstance(rate, (int, float)):
                    rate_str = f"{rate:.2f}%"
                else:
                    rate_str = str(rate)
                print(f"  - {term}: {rate_str}  |  {product}")
                total_offers += 1
            print("-" * 40)

        if errors:
            print("Errors:")
            for b, err in errors.items():
                print(f"  {b}: {err}")
            print("-" * 40)

        return {"status": "success", "banks": len(banks), "offers": total_offers}

    def _load_data(self, file_path: Optional[str]) -> Optional[Dict[str, Any]]:
        path: Optional[Path] = None
        if file_path:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
        else:
            # pick latest in default_dir
            if not self.default_dir.exists():
                return None
            candidates = sorted(self.default_dir.glob("fd_rates_*.json"))
            if not candidates:
                return None
            path = candidates[-1]

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
