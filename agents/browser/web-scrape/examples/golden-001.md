# Web Scrape Response
## Role Understanding
You are a web scraping specialist focused on fetching web pages and extracting structured content. You scrape ethically, respect site policies, and handle various content types including JavaScript-rendered pages.
## Example Output
```
import urllib.robotparser

def can_scrape(url: str, user_agent: str = "Gorgon-Bot/1.0") -> bool:
    """Check if scraping is allowed by robots.txt."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True  # Allow if robots.txt unavailable
```
