from json import dump
from os import path
from datetime import datetime
from bs4 import BeautifulSoup
from requests import get as request_get
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, Playwright
from src.agent1_search.config import load_config
from src.common.logs import log_message
from src.common.path import get_full_path

class NewsScraper:
    def __init__(self, log_path=None):
        self.config = load_config()
        self.RAW_DATA_DIR = get_full_path(self.config["paths"]["output"])
        self.READABLE_PATH = get_full_path(self.config["paths"]["readability"])

        if log_path:
            self.logs = log_path
        else:
            self.logs = self.config["logs"]

    def scrape_news(self, url, playwright: Playwright):
        """
        Fetches the title and body of an individual news article by visiting its URL.
        Uses Readability.js to parse the content and extract both title and textContent.
        """
        try:
            # Load Readability.js
            with open(self.READABLE_PATH, "r", encoding="utf-8") as f:
                readability_js = f.read()

        except Exception:
            log_message(f"Error: Readability.js is not imported", self.logs, log_level="ERROR")
            raise ImportError
        
        try:
            
            # Open page
            chromium = playwright.chromium
            browser = chromium.launch()
            page = browser.new_page()
            REQUEST_TIMEOUT = self.config["http_requests"]["request_timeout"]
            page.goto(url, timeout=REQUEST_TIMEOUT)

            # Inject Readability.js
            page.evaluate(readability_js)

            # Use Readability.js to extract article details
            article = page.evaluate("""
                () => {
                        const reader = new Readability(document);
                        const parsed = reader.parse();
                        if (parsed) {
                            return {
                                title: parsed.title || "No title available",
                                textContent: parsed.textContent || "No content available"
                            };
                        }
                        return null;
                        }
                    """)

            # Close the browser
            browser.close()

            # Return the extracted article details or fallback message
            if article:
                return article["title"].strip(), article["textContent"].strip()
            return "No title available","No content available"

        except Exception as e:
            log_message(f"Error: Could not fetch content from {url}: {e}", self.logs, log_level="WARNING")
            return "Error fetching title", "Error fetching content"
        
    def scrape_site(self, site):
        """
        Scrapes a single site based on the configuration, including the content of each news article.
        """
        try:
            HEADERS = self.config["http_requests"]["headers"]
            REQUEST_TIMEOUT = self.config["http_requests"]["request_timeout"]
            response = request_get(site["url"], headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the containers with news
            containers = soup.select(site["news_container"])
            if not containers:
                log_message(f"Error: Could not find containers for {site['name']}", self.logs, log_level="ERROR")
                return []

            scraped_news = []
            processed_links = set()
            base_url = site["url"]

            for container in containers:
                # Extract news items
                link = container.find(site["link_tag"])
                if link:
                    # Get the link and resolve relative URLs
                    news_link = link.get(site["link_attr"])
                    if not news_link:
                        continue
                    news_link = urljoin(base_url, news_link)

                    # Skip duplicates
                    if news_link in processed_links:
                        continue
                    processed_links.add(news_link)

                    with sync_playwright() as playwright:
                        news_title, news_content = self.scrape_news(news_link, playwright)

                    news_data = {
                        "title": news_title,
                        "link": news_link,
                        "content": news_content,
                        "source": site["name"],
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                    scraped_news.append(news_data)

            return scraped_news

        except Exception as e:
            log_message(f"Error: Could not scrape {site['name']}: {e}", self.logs, log_level="ERROR")
            return []
        
    def save_scraped_news(self, all_sites):
        """
        Save the scraped news into a processed JSON file.
        """
        # Save the scraped news to a JSON file
        output_file = path.join(self.RAW_DATA_DIR, f"scraped_news_{datetime.now().strftime('%Y%m%d')}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            dump(all_sites, f, indent=4, ensure_ascii=False)

        log_message(f"Scraped news saved to {output_file}", self.logs)

    def run_scraper(self):
        """
        Main method to scrape all sites and save the results.
        """
        all_news = []
        for site in self.config["sites"]:
            log_message(f"Scraping {site['name']}...", self.logs)
            all_news.extend(self.scrape_site(site))

        log_message("Saving scraped news...", self.logs)
        self.save_scraped_news(all_news)

        log_message("Newsletter scraping complete.", self.logs)