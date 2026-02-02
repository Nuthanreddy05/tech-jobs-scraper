#!/usr/bin/env python3
"""
PRODUCTION CAREER PAGE SCRAPER V2
==================================
Orchestrates multiple scraping strategies:
1. Greenhouse API (40+ companies, easiest)
2. Lever API (5+ companies, easy)
3. Custom scrapers (TODO: Amazon, Google, etc.)

Runs in GitHub Actions hourly.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add scrapers directory to path
sys.path.insert(0, str(Path(__file__).parent / "scrapers"))

from greenhouse_scraper import GreenhouseScraper
from lever_scraper import LeverScraper


class ProductionScraper:
    """Production-ready career page scraper."""

    def __init__(self, output_dir: str = "jobs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.all_jobs = []

    def scrape_all(self):
        """Run all scrapers in priority order."""
        print("=" * 70)
        print("🚀 PRODUCTION CAREER PAGE SCRAPER V2")
        print("=" * 70)
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Phase 1: Greenhouse API (fastest, most reliable)
        print("\n" + "=" * 70)
        print("PHASE 1: GREENHOUSE API SCRAPING")
        print("=" * 70)
        greenhouse = GreenhouseScraper()
        greenhouse_jobs = greenhouse.scrape_all_companies()
        self.all_jobs.extend(greenhouse_jobs)

        # Phase 2: Lever API
        print("\n" + "=" * 70)
        print("PHASE 2: LEVER API SCRAPING")
        print("=" * 70)
        lever = LeverScraper()
        lever_jobs = lever.scrape_all_companies()
        self.all_jobs.extend(lever_jobs)

        # Phase 3: Custom scrapers (TODO)
        # This would include Amazon, Google, Microsoft, etc.
        # Requires Playwright - implement if needed

        # Print final summary
        self.print_summary()

        # Save results
        self.save_results()

    def print_summary(self):
        """Print final statistics."""
        print("\n" + "=" * 70)
        print("📊 FINAL SUMMARY")
        print("=" * 70)

        # Count by portal type
        greenhouse_count = len([j for j in self.all_jobs if j.get("portal") == "greenhouse"])
        lever_count = len([j for j in self.all_jobs if j.get("portal") == "lever"])

        print(f"Greenhouse jobs:         {greenhouse_count}")
        print(f"Lever jobs:              {lever_count}")
        print(f"TOTAL JOBS:              {len(self.all_jobs)}")
        print()

        # Count by company (top 10)
        company_counts = {}
        for job in self.all_jobs:
            company = job.get("company", "Unknown")
            company_counts[company] = company_counts.get(company, 0) + 1

        print("Top 10 Companies by Job Count:")
        for i, (company, count) in enumerate(sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10], 1):
            print(f"  {i:2d}. {company:30s} {count:3d} jobs")

        print("=" * 70)

    def save_results(self):
        """Save all jobs to structured folders."""
        if not self.all_jobs:
            print("\n⚠️  No jobs to save!")
            return

        print(f"\n💾 Saving {len(self.all_jobs)} jobs...")

        # Save master JSON
        master_json = self.output_dir / "all_jobs.json"
        with open(master_json, 'w') as f:
            json.dump(self.all_jobs, f, indent=2)
        print(f"   ✅ Master JSON: {master_json}")

        # Create individual job folders
        for i, job in enumerate(self.all_jobs, 1):
            job_dir = self.output_dir / f"job_{i:04d}"
            job_dir.mkdir(exist_ok=True)

            # Save metadata
            meta = {
                "company": job.get("company"),
                "title": job.get("title"),
                "location": job.get("location"),
                "url": job.get("url"),
                "portal": job.get("portal"),
                "job_id": job.get("job_id"),
                "scraped_at": datetime.now().isoformat()
            }

            with open(job_dir / "meta.json", 'w') as f:
                json.dump(meta, f, indent=2)

            # Save apply URL
            with open(job_dir / "apply_url.txt", 'w') as f:
                f.write(job.get("url", ""))

            # Save job description
            with open(job_dir / "JD.txt", 'w') as f:
                f.write(f"Job: {job.get('title')}\n")
                f.write(f"Company: {job.get('company')}\n")
                f.write(f"Location: {job.get('location')}\n")
                f.write(f"Portal: {job.get('portal')}\n")
                f.write(f"\nApply: {job.get('url')}\n\n")
                f.write(f"Description:\n{job.get('description', '[Visit URL for full description]')}\n")

            if i % 25 == 0:
                print(f"   Created {i} folders...")

        print(f"   ✅ Created {len(self.all_jobs)} job folders")

        # Create summary CSV for easy viewing
        import csv
        csv_path = self.output_dir / "jobs_summary.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['company', 'title', 'location', 'portal', 'url'])
            writer.writeheader()
            for job in self.all_jobs:
                writer.writerow({
                    'company': job.get('company'),
                    'title': job.get('title'),
                    'location': job.get('location'),
                    'portal': job.get('portal'),
                    'url': job.get('url')
                })
        print(f"   ✅ CSV summary: {csv_path}")

        print(f"\n✅ SCRAPING COMPLETE!")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        print(f"🎯 Total jobs saved: {len(self.all_jobs)}")


def main():
    """Main entry point."""
    scraper = ProductionScraper()
    scraper.scrape_all()


if __name__ == "__main__":
    main()
