# Bot Template & Guidelines

Create your bot under `bots/<your_bot_name>/__init__.py` with a `Bot` class.

## Minimal Example
```python
# bots/my_bot/__init__.py
import json
from datetime import datetime

class Bot:
    name = "my_bot"
    description = "Describe what this bot does"
    author = "Your Name"
    version = "1.0.0"

    def __init__(self):
        self.output_dir = "data/my_bot"

    def run(self, *args):
        # TODO: implement your scraping/RPA
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        payload = {
            "status": "success",
            "scraped_at": datetime.utcnow().isoformat(),
            "args": list(args),
            "items": [],
        }
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out = f"{self.output_dir}/result_{ts}.json"
        with open(out, "w") as f:
            json.dump(payload, f, indent=2)
        return {"output_file": out, "items": len(payload["items"]) }

    def analyze(self, data):
        # Optional post-processing/analytics
        return {"note": "No analysis implemented"}
```

## Recommendations
- **HTTP requests**: use `requests` with timeouts and headers
- **Parsing**: use `beautifulsoup4`
- **Automation (RPA)**: use `selenium` and `webdriver-manager`
- **Delays**: `time.sleep()` between requests to be polite
- **Config**: read from `.env` using `python-dotenv` for secrets

## Parameters
- CLI passes `--params` as positional args to `run()`.
- Integers are auto-coerced by `app.py`, others remain strings.

## Output Format
- Prefer writing JSON under `data/<bot_name>/` with a timestamp.
- Return a small dict summary from `run()` (counts, output_file path).
