#!/usr/bin/env python3
"""
GREENHOUSE API SCRAPER
======================
Scrapes jobs from 40+ companies using Greenhouse's public JSON API.

Companies: OpenAI, Anthropic, Stripe, Uber, Netflix, Airbnb, Dropbox,
           Atlassian, Reddit, Pinterest, Zoom, Snap, etc.

API: https://boards-api.greenhouse.io/v1/boards/{company}/jobs
"""

import requests
import time
from typing import List, Dict, Optional


class GreenhouseScraper:
    """Scrapes jobs from Greenhouse-powered career pages."""

    def __init__(self):
        self.base_url = "https://boards-api.greenhouse.io/v1/boards"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        })

    def get_company_jobs(self, company_slug: str, company_name: str) -> List[Dict]:
        """
        Fetch jobs for a company from Greenhouse API.

        Args:
            company_slug: Greenhouse board ID (e.g., 'anthropic')
            company_name: Display name (e.g., 'Anthropic')

        Returns:
            List of job dictionaries
        """
        print(f"\n🔍 Scraping {company_name} (Greenhouse)...")

        try:
            url = f"{self.base_url}/{company_slug}/jobs"
            response = self.session.get(url, timeout=15)

            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code}")
                return []

            data = response.json()
            jobs = data.get("jobs", [])

            print(f"   ✅ Found {len(jobs)} total jobs")

            # Parse and filter jobs
            parsed_jobs = []
            for job in jobs:
                parsed = self.parse_job(job, company_name)
                if parsed and self.is_tech_role(parsed) and self.is_us_location(parsed):
                    parsed_jobs.append(parsed)

            print(f"   ✅ {len(parsed_jobs)} software/data jobs in US")
            return parsed_jobs

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:80]}")
            return []

    def parse_job(self, job: Dict, company_name: str) -> Dict:
        """Parse Greenhouse job JSON into standard format."""
        try:
            return {
                "company": company_name,
                "title": job.get("title", ""),
                "location": job.get("location", {}).get("name", "Unknown"),
                "url": job.get("absolute_url", ""),
                "job_id": str(job.get("id", "")),
                "departments": [d.get("name", "") for d in job.get("departments", [])],
                "description": job.get("content", ""),
                "portal": "greenhouse",
                "company_slug": str(job.get("id", "")).split("-")[0] if job.get("id") else ""
            }
        except Exception as e:
            print(f"      ⚠️  Parse error: {str(e)[:50]}")
            return {}

    def is_tech_role(self, job: Dict) -> bool:
        """Check if job is software/data related."""
        title = job.get("title", "").lower()
        departments = " ".join(job.get("departments", [])).lower()

        tech_keywords = [
            "software", "engineer", "developer", "backend", "frontend",
            "full stack", "fullstack", "data", "scientist", "analyst",
            "machine learning", "ml", "ai", "artificial intelligence",
            "devops", "sre", "site reliability", "platform", "infrastructure",
            "cloud", "systems"
        ]

        text = f"{title} {departments}"
        return any(kw in text for kw in tech_keywords)

    def is_us_location(self, job: Dict) -> bool:
        """Check if location is in US."""
        location = job.get("location", "").lower()

        if not location or location == "unknown":
            return True  # Assume US if not specified

        us_keywords = [
            "united states", "usa", "us", "remote", "anywhere",
            # States
            "california", "texas", "new york", "florida", "washington",
            "massachusetts", "illinois", "georgia", "virginia", "pennsylvania",
            "colorado", "oregon", "north carolina", "arizona",
            # Cities
            "san francisco", "seattle", "austin", "boston", "nyc", "new york",
            "los angeles", "chicago", "atlanta", "denver", "portland",
            "san jose", "palo alto", "mountain view", "sunnyvale", "redmond"
        ]

        # Check for US indicators
        if any(kw in location for kw in us_keywords):
            return True

        # Exclude international locations
        intl_keywords = [
            "india", "china", "singapore", "london", "uk", "canada",
            "germany", "france", "japan", "australia", "israel"
        ]

        if any(kw in location for kw in intl_keywords):
            return False

        # Default to True for ambiguous cases
        return True

    def scrape_all_companies(self) -> List[Dict]:
        """Scrape all Greenhouse companies."""
        print("=" * 70)
        print("🏢 GREENHOUSE API SCRAPER")
        print("=" * 70)

        # Greenhouse companies (company_slug: company_name)
        companies = {
            # AI/ML Companies
            "anthropic": "Anthropic",
            "openai": "OpenAI",
            "scaleai": "Scale AI",
            "huggingface": "Hugging Face",
            "cohere": "Cohere",

            # Top Tech Companies
            "uber": "Uber",
            "netflix": "Netflix",
            "airbnb": "Airbnb",
            "stripe": "Stripe",
            "databricks": "Databricks",
            "dropbox": "Dropbox",
            "atlassian": "Atlassian",
            "reddit": "Reddit",
            "pinterest": "Pinterest",
            "zoom": "Zoom",
            "snap": "Snap",
            "snowflake": "Snowflake",

            # Fintech
            "plaid": "Plaid",
            "brex": "Brex",
            "robinhood": "Robinhood",
            "coinbase": "Coinbase",
            "chime": "Chime",

            # Productivity & Tools
            "notion": "Notion",
            "figma": "Figma",
            "canva": "Canva",
            "airtable": "Airtable",
            "miro": "Miro",

            # E-commerce & Marketplace
            "instacart": "Instacart",
            "doordash": "DoorDash",
            "shopify": "Shopify",

            # Cloud & Infrastructure
            "cloudflare": "Cloudflare",
            "datadog": "Datadog",
            "mongodb": "MongoDB",
            "elastic": "Elastic",

            # Healthcare & Biotech
            "modernhealth": "Modern Health",
            "tempus": "Tempus",

            # Gaming & Entertainment
            "roblox": "Roblox",
            "unity": "Unity",

            # Other Tech
            "webflow": "Webflow",
            "vercel": "Vercel",
            "grammarly": "Grammarly",
            "duolingo": "Duolingo",
        }

        all_jobs = []
        successful = 0

        for slug, name in companies.items():
            jobs = self.get_company_jobs(slug, name)
            all_jobs.extend(jobs)

            if jobs:
                successful += 1

            # Rate limiting
            time.sleep(2)

        print("\n" + "=" * 70)
        print(f"📊 GREENHOUSE SCRAPING COMPLETE")
        print("=" * 70)
        print(f"Companies attempted:     {len(companies)}")
        print(f"Companies succeeded:     {successful}")
        print(f"Total jobs found:        {len(all_jobs)}")
        print("=" * 70)

        return all_jobs


if __name__ == "__main__":
    scraper = GreenhouseScraper()
    jobs = scraper.scrape_all_companies()

    print(f"\n✅ Final result: {len(jobs)} software/data jobs from Greenhouse")

    # Print sample
    if jobs:
        print("\n📋 Sample jobs:")
        for job in jobs[:5]:
            print(f"   • {job['company']}: {job['title']} ({job['location']})")
