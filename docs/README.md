# Scraping & RPA Station Docs

This folder contains usage instructions for the scraping/RPA station.

## Contents

- `README.md` (you are here): Quick start
- `bot_template.md`: How to create a new bot
- `scheduling.md`: How to schedule bots (cron, Python schedule)

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
