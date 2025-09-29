# Scraping & RPA Station Docs

This folder contains usage instructions for the scraping/RPA station.

## Contents

- `README.md` (you are here): Quick start
- `bot_template.md`: How to create a new bot
- `scheduling.md`: How to schedule bots (cron, Python schedule)
 - `site_mapper.md`: How to crawl and map a website (experimental)

## Quick Start

1) Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # zsh/bash
# or use explicit paths without activating:
# ./venv/bin/python ...
```

2) Install dependencies
```bash
./venv/bin/pip install -r requirements.txt
```

3) List available bots
```bash
./venv/bin/python app.py list
```

4) Run a bot
```bash
# Example: Hacker News top, fetch 5 items
./venv/bin/python app.py run hackernews_top --params 5

# Example: Amazon deals, category "electronics" and limit 10
./venv/bin/python app.py run amazon_deals --params electronics 10

# Example: Site Mapper (experimental)
# Crawl https://example.com to depth 1, restrict to same domain
./venv/bin/python app.py run site_mapper --params https://example.com 1 true
```

5) Where outputs go
- JSON files are saved under `data/<bot_name>/` with timestamps.

## Adding a New Bot (see `bot_template.md`)
- Create a folder under `bots/<your_bot_name>/`
- Put an `__init__.py` with a `Bot` class implementing `run()`
- Optional `analyze()` method for post-processing

## Troubleshooting
- If `python app.py list` shows no bots:
  - Ensure the `bots/` directory exists and each bot has an `__init__.py` containing a `Bot` class.
- If a website blocks scraping, add headers, timeouts, and delays. Respect robots.txt and ToS.

## Notes on Site Mapper (experimental)
- The `site_mapper` bot prints a list of discovered URLs grouped by depth and a Mermaid diagram showing link relationships.
- It also attempts to list potential unexposed routes from `sitemap.xml`.
- Important: Real-world usefulness has NOT been verified on complex or internal sites. Treat results as indicative only. See `docs/site_mapper.md` for details.
