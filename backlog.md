# Backlog

## Thai Fixed Deposits scraper accuracy
- The current scraped data and CLI report produced by `bots/thai_fixed_deposits/` and `bots/thai_fd_report/` are not reliably accurate to real bank offers.
- Root cause: Generic HTML parsing (tables/blocks + regex) can capture unrelated text and miss dynamic content. Bank pages vary and may require bank-specific selectors or JS rendering.

### Actions required (future work)
- Implement per-bank, selector-specific parsers for:
  - `bangkok_bank`
  - `kasikorn`
  - `gh_bank`
- Add robust term normalization (e.g., 3M/6M/12M vs Thai text like "3 เดือน", "1 ปี").
- Constrain scrape scope to official rate sections; ignore marketing content.
- Add Selenium (or Playwright) fallback for dynamic pages when needed.
- Add tests with small saved HTML fixtures for each bank to detect breakage.
- Add schema validation (e.g., interest rate bounds, expected term sets) to catch anomalies.
- Optionally integrate manual guidance/config (CSS/XPath per bank) that can be updated without code changes.

### Temporary note
Until the above is implemented, treat outputs as indicative only and cross-check against official bank pages.
