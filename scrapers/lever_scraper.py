#!/usr/bin/env python3
"""
LEVER API SCRAPER
=================
Scrapes jobs from companies using Lever's public JSON API.

Companies: Character.AI, and other Lever-powered companies

API: https://api.lever.co/v0/postings/{company}
"""

import requests
import time
from typing import List, Dict


class LeverScraper:
    """Scrapes jobs from Lever-powered career pages."""

    def __init__(self):
        self.base_url = "https://api.lever.co/v0/postings"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        })

    def get_company_jobs(self, company_slug: str, company_name: str) -> List[Dict]:
        """
        Fetch jobs for a company from Lever API.

        Args:
            company_slug: Lever company ID (e.g., 'character')
            company_name: Display name (e.g., 'Character.AI')

        Returns:
            List of job dictionaries
        """
        print(f"\n🔍 Scraping {company_name} (Lever)...")

        try:
            url = f"{self.base_url}/{company_slug}"
            response = self.session.get(url, timeout=15)

            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code}")
                return []

            jobs = response.json()

            if not isinstance(jobs, list):
                print(f"   ⚠️  Unexpected response format")
                return []

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
        """Parse Lever job JSON into standard format."""
        try:
            # Extract location
            location = "Unknown"
            if job.get("categories", {}).get("location"):
                location = job["categories"]["location"]
            elif job.get("workplaceType"):
                location = job["workplaceType"]

            return {
                "company": company_name,
                "title": job.get("text", ""),
                "location": location,
                "url": job.get("hostedUrl", ""),
                "job_id": job.get("id", ""),
                "team": job.get("categories", {}).get("team", ""),
                "commitment": job.get("categories", {}).get("commitment", ""),
                "description": job.get("description", ""),
                "portal": "lever"
            }
        except Exception as e:
            print(f"      ⚠️  Parse error: {str(e)[:50]}")
            return {}

    def is_tech_role(self, job: Dict) -> bool:
        """Check if job is software/data related."""
        title = job.get("title", "").lower()
        team = job.get("team", "").lower()

        tech_keywords = [
            "software", "engineer", "developer", "backend", "frontend",
            "full stack", "fullstack", "data", "scientist", "analyst",
            "machine learning", "ml", "ai", "artificial intelligence",
            "devops", "sre", "site reliability", "platform", "infrastructure",
            "cloud", "systems"
        ]

        text = f"{title} {team}"
        return any(kw in text for kw in tech_keywords)

    def is_us_location(self, job: Dict) -> bool:
        """Check if location is in US."""
        location = job.get("location", "").lower()

        if not location or location == "unknown":
            return True

        us_keywords = [
            "united states", "usa", "us", "remote", "anywhere",
            "california", "texas", "new york", "florida", "washington",
            "massachusetts", "seattle", "san francisco", "austin", "boston"
        ]

        if any(kw in location for kw in us_keywords):
            return True

        intl_keywords = ["india", "china", "singapore", "london", "uk", "canada"]
        if any(kw in location for kw in intl_keywords):
            return False

        return True

    def scrape_all_companies(self) -> List[Dict]:
        """Scrape all Lever companies."""
        print("=" * 70)
        print("🏢 LEVER API SCRAPER")
        print("=" * 70)

        # Lever companies (company_slug: company_name)
        companies = {
            "character": "Character.AI",
            "lattice": "Lattice",
            "gusto": "Gusto",
            "niantic": "Niantic",
            "peloton": "Peloton",
        }

        all_jobs = []
        successful = 0

        for slug, name in companies.items():
            jobs = self.get_company_jobs(slug, name)
            all_jobs.extend(jobs)

            if jobs:
                successful += 1

            time.sleep(2)

        print("\n" + "=" * 70)
        print(f"📊 LEVER SCRAPING COMPLETE")
        print("=" * 70)
        print(f"Companies attempted:     {len(companies)}")
        print(f"Companies succeeded:     {successful}")
        print(f"Total jobs found:        {len(all_jobs)}")
        print("=" * 70)

        return all_jobs


if __name__ == "__main__":
    scraper = LeverScraper()
    jobs = scraper.scrape_all_companies()

    print(f"\n✅ Final result: {len(jobs)} software/data jobs from Lever")

    if jobs:
        print("\n📋 Sample jobs:")
        for job in jobs[:5]:
            print(f"   • {job['company']}: {job['title']} ({job['location']})")
