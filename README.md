# Web Scraping & RPA Station

A modular and extensible web scraping and RPA (Robotic Process Automation) station built with Python. Easily create, manage, and run web scraping bots and automation tasks.

## Features

- **Modular Bot System**: Each bot is self-contained in its own directory
- **Easy to Extend**: Create new bots by following the template
- **Built-in Bots**: Comes with sample bots for common scraping tasks
- **Simple CLI**: Manage and run bots through a command-line interface
- **Data Storage**: Automatically saves scraped data with timestamps
- **Analysis Tools**: Built-in functions to analyze scraped data

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd scraper-kit
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### List Available Bots

```bash
python app.py list
```

### Run a Bot

```bash
python app.py run <bot_name> [--params param1 param2 ...]
```

### Example: Run HackerNews Top Stories Bot

```bash
python app.py run hackernews_top --params 5
```

### Example: Run Amazon Deals Bot

```bash
python app.py run amazon_deals --params electronics 10
```

## Included Bots

### 1. HackerNews Top Stories
- **Name**: `hackernews_top`
- **Description**: Fetches the top stories from Hacker News
- **Parameters**: 
  - `limit` (optional): Number of stories to fetch (default: 10)

### 2. Amazon Deals
- **Name**: `amazon_deals`
- **Description**: Scrapes deals from Amazon's Today's Deals page
- **Parameters**:
  - `category` (optional): Category to filter deals (e.g., 'electronics', 'books')
  - `limit` (optional): Maximum number of deals to fetch (default: 10)

### 3. Thai Fixed Deposits
- **Name**: `thai_fixed_deposits`
- **Description**: Scrapes fixed/time-deposit interest rates from major Thai banks (e.g., Bangkok Bank, Kasikornbank, GH Bank) and outputs normalized data for comparison.
- **Parameters**:
  - `[banks...]` (optional positional): One or more bank keys to scrape. Defaults to all supported banks.
    - Supported keys: `bangkok_bank`, `kasikorn`, `gh_bank`

#### Example: Run Thai Fixed Deposits Bot

```bash
python app.py run thai_fixed_deposits
# or specific banks
python app.py run thai_fixed_deposits --params bangkok_bank kasikorn
```

### 4. Thai Fixed Deposits Report
- **Name**: `thai_fd_report`
- **Description**: Reads the latest JSON from `thai_fixed_deposits` and prints a CLI report of banks and their offers (term, rate, product).
- **Parameters**:
  - `file_path` (optional): Path to a specific JSON file; defaults to the latest in `data/thai_fixed_deposits/`.

#### Example: Run Thai Fixed Deposits Report

```bash
python app.py run thai_fd_report
# or specify a file
python app.py run thai_fd_report --params data/thai_fixed_deposits/fd_rates_YYYYMMDD_HHMMSS.json
```

### 5. Site Mapper
- **Name**: `site_mapper`
- **Description**: Crawls from a start URL up to a depth, prints a list of discovered URLs grouped by depth, plus a Mermaid diagram of the site graph. Also lists potential unexposed routes from sitemap.xml.
- **Parameters**:
  - `start_url` (required): Starting page to crawl
  - `max_depth` (optional, default `2`): Crawl depth
  - `same_domain_only` (optional, default `true`): Restrict to the same host

#### Example: Run Site Mapper

```bash
python app.py run site_mapper --params https://example.com 1 true
```

## Creating a New Bot

1. Create a new directory in the `bots` folder with your bot's name
2. Create an `__init__.py` file in that directory
3. Implement your bot by creating a class named `Bot` with at least a `run()` method

Example bot structure:

```python
class Bot:
    name = "my_bot"
    description = "Description of what this bot does"
    author = "Your Name"
    version = "1.0.0"
    
    def __init__(self):
        # Initialize any required resources
        pass
        
    def run(self, *args, **kwargs):
        """
        Main method that gets called when the bot is executed
        """
        # Your bot's code here
        return {"status": "success", "message": "Bot completed successfully"}
        
    def analyze(self, data):
        """
        Optional: Add analysis methods for the scraped data
        """
        return {"analysis": "Example analysis"}
```

## Best Practices

1. **Rate Limiting**: Be respectful of websites by adding delays between requests
2. **Error Handling**: Implement proper error handling and logging
3. **User-Agent Rotation**: Rotate user agents to avoid detection
4. **Proxies**: Use proxy servers for large-scale scraping
5. **Respect robots.txt**: Check and respect the website's robots.txt file

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
