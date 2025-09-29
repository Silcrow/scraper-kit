# Scheduling Bots

You can run bots on a schedule using cron (recommended on macOS/Linux) or a Python scheduler.

## Cron

1) Edit crontab:
```bash
crontab -e
```

2) Example: run `hackernews_top` every hour
```cron
0 * * * * /bin/bash -lc 'cd /Users/youruser/yourproject && ./venv/bin/python app.py run hackernews_top --params 10 >> logs/cron.log 2>&1'
```
- Ensure full paths and that the virtualenv is used.

## Python `schedule`

Create a small runner (example `scheduler.py`):
```python
import schedule
import time
import subprocess

CMD = ["./venv/bin/python", "app.py", "run", "hackernews_top", "--params", "10"]

def job():
    subprocess.run(CMD, check=False)

schedule.every().hour.at(":00").do(job)

while True:
    schedule.run_pending()
    time.sleep(5)
```

Run:
```bash
./venv/bin/python scheduler.py
```
