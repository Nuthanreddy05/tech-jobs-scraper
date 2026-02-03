#!/usr/bin/env python3
"""
WORKDAY API SCRAPER
===================
Scrapes jobs from companies using Workday's ATS platform.

Companies: Amazon, Microsoft, Apple, Netflix, Goldman Sachs, JPMorgan,
           Accenture, Deloitte, Adobe, Salesforce, and 40+ more

Workday is used by 200+ Fortune 500 companies. This scraper unlocks
access to the biggest employers in tech, finance, and consulting.

API: POST https://{company}.wd5.myworkdayjobs.com/wday/cxs/{company}/{site}/jobs
"""

import requests
import time
from datetime import datetime
from typing import List, Dict


class WorkdayScraper:
    """Scrapes jobs from Workday-powered career pages."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def scrape_company(self, company_config: Dict) -> List[Dict]:
        """
        Scrape a single Workday company.

        Args:
            company_config: Dict with 'name', 'tenant', 'site'

        Returns:
            List of job dictionaries
        """
        company_name = company_config['name']
        tenant = company_config['tenant']
        site = company_config['site']

        print(f"\n🔍 Scraping {company_name} (Workday)...")

        try:
            # Workday API endpoint
            url = f"https://{tenant}.wd5.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"

            # Request payload
            payload = {
                "appliedFacets": {},
                "limit": 20,
                "offset": 0,
                "searchText": ""
            }

            jobs_collected = []
            offset = 0
            max_pages = 10  # Limit to 200 jobs per company

            while offset < max_pages * 20:
                payload['offset'] = offset

                response = self.session.post(url, json=payload, timeout=15)

                if response.status_code != 200:
                    print(f"   ⚠️  HTTP {response.status_code}")
                    break

                data = response.json()
                job_postings = data.get('jobPostings', [])

                if not job_postings:
                    break  # No more jobs

                # Parse jobs
                for job in job_postings:
                    parsed = self.parse_job(job, company_name, tenant, site)
                    if parsed and self.is_tech_role(parsed) and self.is_us_location(parsed):
                        jobs_collected.append(parsed)

                # Check if there are more pages
                total_jobs = data.get('total', 0)
                if offset + 20 >= total_jobs:
                    break

                offset += 20
                time.sleep(1)  # Rate limiting

            print(f"   ✅ {len(jobs_collected)} software/data jobs in US")
            return jobs_collected

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:80]}")
            return []

    def parse_job(self, job: Dict, company_name: str, tenant: str, site: str) -> Dict:
        """Parse Workday job JSON into standard format."""
        try:
            # Extract location
            location = "Unknown"
            if job.get('locationsText'):
                location = job['locationsText']
            elif job.get('bulletFields'):
                for field in job['bulletFields']:
                    if 'Location' in str(field):
                        location = str(field).replace('Location:', '').strip()

            # Build full URL
            external_path = job.get('externalPath', '')
            job_url = f"https://{tenant}.wd5.myworkdayjobs.com/{site}{external_path}"

            # Extract job ID from path
            job_id = external_path.split('/')[-1] if external_path else job.get('bulletFields', [''])[0]

            return {
                "company": company_name,
                "title": job.get('title', ''),
                "location": location,
                "url": job_url,
                "job_id": str(job_id),
                "description": job.get('text', ''),  # Workday provides limited description in API
                "portal": "workday",
                "posted_at": job.get('postedOn', ''),  # ✅ Workday provides real posting date!
                "scraped_at": datetime.utcnow().isoformat() + "Z",
                "time_type": job.get('timeType', ''),
                "tenant": tenant,
                "site": site
            }
        except Exception as e:
            print(f"      ⚠️  Parse error: {str(e)[:50]}")
            return {}

    def is_tech_role(self, job: Dict) -> bool:
        """Check if job is software/data related."""
        title = job.get('title', '').lower()

        tech_keywords = [
            "software", "engineer", "developer", "backend", "frontend",
            "full stack", "fullstack", "data", "scientist", "analyst",
            "machine learning", "ml", "ai", "artificial intelligence",
            "devops", "sre", "site reliability", "platform", "infrastructure",
            "cloud", "systems", "security", "architect", "technical"
        ]

        return any(kw in title for kw in tech_keywords)

    def is_us_location(self, job: Dict) -> bool:
        """Check if location is in US."""
        location = job.get('location', '').lower()

        if not location or location == "unknown":
            return True  # Assume US if not specified

        us_indicators = [
            "united states", "usa", "u.s.", "remote", "california", "new york",
            "texas", "washington", "seattle", "san francisco", "austin",
            "boston", "chicago", "denver", "portland", "los angeles",
            "palo alto", "mountain view", "sunnyvale", "santa clara"
        ]

        non_us_indicators = [
            "india", "canada", "uk", "london", "europe", "asia", "china",
            "bangalore", "hyderabad", "toronto", "dublin", "berlin"
        ]

        # Exclude non-US
        if any(indicator in location for indicator in non_us_indicators):
            return False

        # Include US
        return any(indicator in location for indicator in us_indicators)

    def scrape_all_companies(self) -> List[Dict]:
        """Scrape all Workday companies."""
        print("=" * 70)
        print("🏢 WORKDAY API SCRAPER")
        print("=" * 70)

        # Top 50 Workday companies
        # Format: {name, tenant (subdomain), site (job board path)}
        companies = [
            # FAANG & Top Tech
            {"name": "Amazon", "tenant": "amazon", "site": "Amazon_University_Jobs"},
            {"name": "Netflix", "tenant": "netflix", "site": "Netflix_External_Site"},
            {"name": "Apple", "tenant": "apple", "site": "Apple_Careers"},

            # Note: Microsoft uses careers.microsoft.com (custom Workday integration)
            # Note: Google, Meta use custom portals (not Workday)

            # Finance - Top H-1B Sponsors
            {"name": "Goldman Sachs", "tenant": "goldmansachs", "site": "External"},
            {"name": "JPMorgan Chase", "tenant": "jpmorganchase", "site": "careers"},
            {"name": "Morgan Stanley", "tenant": "morganstanley", "site": "careers"},
            {"name": "Bank of America", "tenant": "bankofamerica", "site": "careers"},
            {"name": "Capital One", "tenant": "capitalone", "site": "careers"},
            {"name": "Wells Fargo", "tenant": "wellsfargo", "site": "external"},

            # Consulting - Huge H-1B Sponsors
            {"name": "Accenture", "tenant": "accenture", "site": "careers"},
            {"name": "Deloitte", "tenant": "deloitte", "site": "DeloitteGlobalCareers"},
            {"name": "PwC", "tenant": "pwc", "site": "Global_Experienced_Careers"},
            {"name": "EY (Ernst & Young)", "tenant": "ey", "site": "EY_Experienced"},
            {"name": "McKinsey & Company", "tenant": "mckinsey", "site": "mckinsey"},

            # Tech Companies on Workday
            {"name": "Adobe", "tenant": "adobe", "site": "external_experienced"},
            {"name": "Salesforce", "tenant": "salesforce", "site": "salesforce"},
            {"name": "ServiceNow", "tenant": "servicenow", "site": "servicenow"},
            {"name": "Qualcomm", "tenant": "qualcomm", "site": "External"},
            {"name": "Nvidia", "tenant": "nvidia", "site": "nvidiacareers"},
            {"name": "Intel", "tenant": "intel", "site": "External"},
            {"name": "VMware", "tenant": "vmware", "site": "vmware"},

            # Healthcare - Good H-1B Sponsors
            {"name": "CVS Health", "tenant": "myworkdayjobs.com/CVSHealth", "site": "CVS_Health"},
            {"name": "UnitedHealth Group", "tenant": "unitedhealthgroup", "site": "External"},
            {"name": "Cigna", "tenant": "cigna", "site": "cigna_careers"},

            # Retail/E-commerce
            {"name": "Target", "tenant": "target", "site": "careers"},
            {"name": "Walmart", "tenant": "walmart", "site": "walmartcareers"},
            {"name": "Best Buy", "tenant": "bestbuy", "site": "BestBuyCareers"},

            # Pharma & Biotech
            {"name": "Pfizer", "tenant": "pfizer", "site": "pfizer"},
            {"name": "Johnson & Johnson", "tenant": "jnj", "site": "External"},
            {"name": "Merck", "tenant": "merck", "site": "External"},

            # Industrial/Manufacturing
            {"name": "Boeing", "tenant": "boeing", "site": "External"},
            {"name": "Lockheed Martin", "tenant": "lockheedmartin", "site": "External"},
            {"name": "General Electric", "tenant": "ge", "site": "careers"},
            {"name": "3M", "tenant": "3m", "site": "Search"},

            # Telecom
            {"name": "Verizon", "tenant": "verizon", "site": "careers"},
            {"name": "T-Mobile", "tenant": "tmobile", "site": "tmobile"},
            {"name": "AT&T", "tenant": "att", "site": "External"},

            # Insurance
            {"name": "State Farm", "tenant": "statefarm", "site": "careers"},
            {"name": "Liberty Mutual", "tenant": "libertymutual", "site": "libertymutualgroup"},

            # Energy
            {"name": "Chevron", "tenant": "chevron", "site": "careers"},
            {"name": "Shell", "tenant": "shell", "site": "shell"},

            # Automotive
            {"name": "Tesla", "tenant": "tesla", "site": "TeslaCareers"},  # May use custom
            {"name": "Ford", "tenant": "ford", "site": "Ford_Motor_Company"},
            {"name": "GM (General Motors)", "tenant": "gm", "site": "External"},

            # Airlines
            {"name": "Delta Air Lines", "tenant": "delta", "site": "External"},
            {"name": "American Airlines", "tenant": "aa", "site": "External"},
            {"name": "United Airlines", "tenant": "ual", "site": "External"},
        ]

        all_jobs = []
        successful = 0

        for config in companies:
            jobs = self.scrape_company(config)
            all_jobs.extend(jobs)

            if jobs:
                successful += 1

            time.sleep(2)  # Rate limiting between companies

        print("\n" + "=" * 70)
        print(f"📊 WORKDAY SCRAPING COMPLETE")
        print("=" * 70)
        print(f"Companies attempted:     {len(companies)}")
        print(f"Companies with jobs:     {successful}")
        print(f"Total jobs collected:    {len(all_jobs)}")
        print("=" * 70)

        return all_jobs


def main():
    """Test the Workday scraper."""
    scraper = WorkdayScraper()
    jobs = scraper.scrape_all_companies()

    print(f"\n✅ Final result: {len(jobs)} software/data jobs from Workday")

    if jobs:
        print("\n📋 Sample jobs:")
        for job in jobs[:5]:
            print(f"   • {job['company']}: {job['title']} ({job['location']})")


if __name__ == "__main__":
    main()
