#!/usr/bin/env python3
"""
CAREER PAGE SCRAPER - RUNS IN GITHUB ACTIONS
=============================================
Scrapes software/data jobs from top tech company career pages.
Runs in GitHub's cloud, bypassing all network restrictions.

Based on research from:
- https://github.com/speedyapply/JobSpy
- https://github.com/anthonyjdella/automated-job-web-scraping
- https://medium.com/@lassebenninga/setup-free-webscraping-in-less-than-5-minutes-using-github-actions-330e1151fbea
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests

# Groq API for AI parsing
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')


class CareerPageScraper:
    """Scrapes jobs from company career pages in GitHub Actions."""

    def __init__(self):
        self.jobs = []
        self.output_dir = Path("jobs")
        self.output_dir.mkdir(exist_ok=True)

    def scrape_with_playwright(self, url: str, company: str) -> list:
        """Scrape page with Playwright."""
        print(f"\n🔍 Scraping {company}: {url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Navigate to page
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(3)  # Wait for JS to load

                # Get page content
                content = page.content()
                browser.close()

                # Parse with AI if available
                if GROQ_API_KEY:
                    jobs = self.parse_with_ai(content, company)
                else:
                    # Simple fallback parsing
                    jobs = self.simple_parse(content, company)

                print(f"   ✅ Found {len(jobs)} jobs")
                return jobs

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            return []

    def parse_with_ai(self, html_content: str, company: str) -> list:
        """Parse HTML with Groq AI."""
        try:
            # Truncate content to fit in context
            content_preview = html_content[:15000]

            prompt = f"""
Extract job postings for {company} from this HTML.
Return ONLY valid JSON array: [{{"title": "...", "location": "...", "url": "..."}}]
Focus on SOFTWARE and DATA engineering roles only.
No markdown formatting.

HTML:
{content_preview}
"""

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Clean markdown if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]

                jobs = json.loads(content.strip())
                return jobs if isinstance(jobs, list) else []

        except Exception as e:
            print(f"      ⚠️ AI parsing failed: {str(e)[:50]}")

        return []

    def simple_parse(self, html_content: str, company: str) -> list:
        """Simple fallback parser."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []

        # Look for common job link patterns
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            href = link['href']

            # Filter for tech roles
            tech_keywords = ['engineer', 'developer', 'data', 'software', 'ml', 'ai']
            if any(kw in text.lower() for kw in tech_keywords) and len(text) > 10:
                jobs.append({
                    "company": company,
                    "title": text,
                    "location": "Unknown",
                    "url": href if href.startswith('http') else f"https://{company.lower().replace(' ', '')}.com{href}"
                })

        return jobs[:50]  # Limit to 50

    def scrape_all_companies(self):
        """Scrape top tech companies."""
        print("=" * 70)
        print("🚀 GITHUB ACTIONS CAREER PAGE SCRAPER")
        print("=" * 70)

        # Top H1B tech companies with career pages
        companies = [
            {"name": "Amazon", "url": "https://www.amazon.jobs/en/search?base_query=software+engineer&loc_query=United+States"},
            {"name": "Google", "url": "https://www.google.com/about/careers/applications/jobs/results/?q=software%20engineer"},
            {"name": "Microsoft", "url": "https://careers.microsoft.com/us/en/search-results?keywords=software%20engineer"},
            {"name": "Meta", "url": "https://www.metacareers.com/jobs?q=software%20engineer"},
            {"name": "Apple", "url": "https://jobs.apple.com/en-us/search?search=software%20engineer&sort=relevance"},
            {"name": "Netflix", "url": "https://jobs.netflix.com/search?q=software"},
            {"name": "Uber", "url": "https://www.uber.com/us/en/careers/list/?query=software"},
            {"name": "Airbnb", "url": "https://careers.airbnb.com/positions/?search=software"},
            {"name": "Stripe", "url": "https://stripe.com/jobs/search?query=software"},
            {"name": "Databricks", "url": "https://www.databricks.com/company/careers/open-positions?department=Engineering"},
        ]

        for company in companies:
            jobs = self.scrape_with_playwright(company["url"], company["name"])

            # Filter for US locations and tech roles
            for job in jobs:
                if self.is_valid_job(job):
                    job["scraped_at"] = datetime.now().isoformat()
                    job["source"] = "career_page"
                    self.jobs.append(job)

            time.sleep(5)  # Rate limiting

        # Save results
        self.save_results()

    def is_valid_job(self, job: dict) -> bool:
        """Validate job is tech role + US location."""
        title = job.get("title", "").lower()
        location = job.get("location", "").lower()

        # Tech keywords
        tech_kw = ["software", "engineer", "developer", "data", "ml", "ai", "devops", "sre"]
        is_tech = any(kw in title for kw in tech_kw)

        # US location (or unknown)
        us_kw = ["us", "united states", "remote", "california", "texas", "new york", "washington"]
        is_us = any(kw in location for kw in us_kw) or location == "unknown"

        return is_tech and is_us

    def save_results(self):
        """Save jobs to JSON and individual folders."""
        print(f"\n💾 Saving {len(self.jobs)} jobs...")

        # Save master JSON
        with open(self.output_dir / "all_jobs.json", 'w') as f:
            json.dump(self.jobs, f, indent=2)

        # Create individual job folders
        for i, job in enumerate(self.jobs, 1):
            job_dir = self.output_dir / f"job_{i:03d}"
            job_dir.mkdir(exist_ok=True)

            # Save job details
            with open(job_dir / "details.json", 'w') as f:
                json.dump(job, f, indent=2)

            # Save apply URL
            with open(job_dir / "apply_url.txt", 'w') as f:
                f.write(job.get("url", ""))

        print(f"   ✅ Saved to {self.output_dir}/")
        print(f"\n✅ COMPLETE: {len(self.jobs)} jobs scraped from career pages!")


if __name__ == "__main__":
    scraper = CareerPageScraper()
    scraper.scrape_all_companies()
