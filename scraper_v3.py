#!/usr/bin/env python3
"""
PRODUCTION CAREER PAGE SCRAPER V3
==================================
Optimized file structure to prevent repo bloat:
- Consolidated daily files instead of per-job folders
- Deduplication to prevent saving same job multiple times
- Clean, scalable structure

Output Structure:
jobs/
  ├── all_jobs.json              # All unique jobs (deduplicated)
  ├── jobs_summary.csv           # Quick overview
  ├── daily/
  │   ├── 2026-02-02.json       # All jobs scraped on this day
  │   └── 2026-02-03.json
  └── by_company/
      ├── anthropic.json         # All Anthropic jobs
      └── openai.json

Runs in GitHub Actions hourly.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import csv

# Add scrapers directory to path
sys.path.insert(0, str(Path(__file__).parent / "scrapers"))

from greenhouse_scraper import GreenhouseScraper
from lever_scraper import LeverScraper
from workday_scraper import WorkdayScraper


class ProductionScraperV3:
    """Production-ready career page scraper with optimized file structure."""

    def __init__(self, output_dir: str = "jobs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Create subdirectories
        (self.output_dir / "daily").mkdir(exist_ok=True)
        (self.output_dir / "by_company").mkdir(exist_ok=True)

        self.all_jobs = []
        self.existing_jobs = self._load_existing_jobs()

    def _load_existing_jobs(self):
        """Load existing jobs for deduplication."""
        master_file = self.output_dir / "all_jobs.json"
        if master_file.exists():
            try:
                with open(master_file, 'r') as f:
                    jobs = json.load(f)
                    print(f"📂 Loaded {len(jobs)} existing jobs for deduplication")
                    return jobs
            except:
                return []
        return []

    def _generate_job_hash(self, job):
        """Generate unique hash for job deduplication."""
        # Use company + job_id as unique identifier
        return f"{job.get('company', '')}_{job.get('job_id', '')}".lower().replace(" ", "_")

    def _deduplicate_jobs(self, new_jobs):
        """Remove duplicate jobs based on company + job_id."""
        existing_hashes = {self._generate_job_hash(job) for job in self.existing_jobs}

        unique_new_jobs = []
        duplicates = 0

        for job in new_jobs:
            job_hash = self._generate_job_hash(job)
            if job_hash not in existing_hashes:
                unique_new_jobs.append(job)
                existing_hashes.add(job_hash)
            else:
                duplicates += 1

        if duplicates > 0:
            print(f"   🔄 Skipped {duplicates} duplicate jobs")

        return unique_new_jobs

    def _enrich_with_freshness(self, new_jobs):
        """Add freshness tracking: first_discovered, hours_old, apply_priority."""
        enriched_jobs = []
        now = datetime.now(datetime.timezone.utc)

        # Build lookup of existing jobs
        existing_lookup = {}
        for job in self.existing_jobs:
            job_hash = self._generate_job_hash(job)
            existing_lookup[job_hash] = job

        for job in new_jobs:
            job_hash = self._generate_job_hash(job)

            # Check if we've seen this job before
            if job_hash in existing_lookup:
                existing = existing_lookup[job_hash]
                # Preserve original discovery time
                job['first_discovered'] = existing.get('first_discovered', now.isoformat() + "Z")
                job['times_seen'] = existing.get('times_seen', 1) + 1
            else:
                # Brand new job - mark when we first discovered it
                job['first_discovered'] = now.isoformat() + "Z"
                job['times_seen'] = 1

            # Calculate age
            first_discovered = datetime.fromisoformat(job['first_discovered'].replace('Z', '+00:00'))
            age_delta = now - first_discovered
            hours_old = age_delta.total_seconds() / 3600
            days_old = age_delta.days

            job['hours_old'] = round(hours_old, 1)
            job['days_old'] = days_old

            # Calculate apply priority based on age
            if hours_old <= 24:
                job['apply_priority'] = 'HIGH'
            elif hours_old <= 48:
                job['apply_priority'] = 'MEDIUM'
            elif hours_old <= 168:  # 7 days
                job['apply_priority'] = 'LOW'
            else:
                job['apply_priority'] = 'EXPIRED'

            # Freshness score (0-100)
            if hours_old <= 24:
                freshness = 100
            elif hours_old <= 48:
                freshness = 75
            elif hours_old <= 168:
                freshness = 50 - (hours_old - 48) / 120 * 30  # Decay from 50 to 20 over 5 days
            else:
                freshness = max(0, 20 - (days_old - 7) * 2)  # Decay after 7 days

            job['freshness_score'] = round(freshness, 1)

            enriched_jobs.append(job)

        return enriched_jobs

    def scrape_all(self):
        """Run all scrapers in priority order."""
        print("=" * 70)
        print("🚀 PRODUCTION CAREER PAGE SCRAPER V3")
        print("=" * 70)
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Phase 1: Greenhouse API (fastest, most reliable)
        print("\n" + "=" * 70)
        print("PHASE 1: GREENHOUSE API SCRAPING")
        print("=" * 70)
        greenhouse = GreenhouseScraper()
        greenhouse_jobs = greenhouse.scrape_all_companies()

        # Phase 2: Lever API
        print("\n" + "=" * 70)
        print("PHASE 2: LEVER API SCRAPING")
        print("=" * 70)
        lever = LeverScraper()
        lever_jobs = lever.scrape_all_companies()

        # Phase 3: Workday API
        print("\n" + "=" * 70)
        print("PHASE 3: WORKDAY API SCRAPING (Amazon, Microsoft, Goldman Sachs, etc.)")
        print("=" * 70)
        workday = WorkdayScraper()
        workday_jobs = workday.scrape_all_companies()

        # Combine all scraped jobs
        all_scraped = greenhouse_jobs + lever_jobs + workday_jobs

        # Deduplicate
        print("\n" + "=" * 70)
        print("🔄 DEDUPLICATION & FRESHNESS TRACKING")
        print("=" * 70)
        print(f"   Total scraped: {len(all_scraped)}")
        unique_jobs = self._deduplicate_jobs(all_scraped)
        print(f"   New unique jobs: {len(unique_jobs)}")

        # Add freshness tracking
        enriched_jobs = self._enrich_with_freshness(unique_jobs)

        # Show freshness breakdown
        high_priority = len([j for j in enriched_jobs if j['apply_priority'] == 'HIGH'])
        medium_priority = len([j for j in enriched_jobs if j['apply_priority'] == 'MEDIUM'])
        low_priority = len([j for j in enriched_jobs if j['apply_priority'] == 'LOW'])

        print(f"\n   📊 Freshness Breakdown:")
        print(f"   HIGH priority (<24h):     {high_priority} jobs 🔥")
        print(f"   MEDIUM priority (24-48h): {medium_priority} jobs")
        print(f"   LOW priority (2-7 days):  {low_priority} jobs")

        self.all_jobs = enriched_jobs

        # Print final summary
        self.print_summary()

        # Save results
        self.save_results()

    def print_summary(self):
        """Print final statistics."""
        print("\n" + "=" * 70)
        print("📊 SCRAPING SUMMARY")
        print("=" * 70)

        # Count by portal type
        greenhouse_count = len([j for j in self.all_jobs if j.get("portal") == "greenhouse"])
        lever_count = len([j for j in self.all_jobs if j.get("portal") == "lever"])
        workday_count = len([j for j in self.all_jobs if j.get("portal") == "workday"])

        print(f"Greenhouse jobs:         {greenhouse_count}")
        print(f"Lever jobs:              {lever_count}")
        print(f"Workday jobs:            {workday_count}")
        print(f"NEW UNIQUE JOBS:         {len(self.all_jobs)}")
        print(f"Total in database:       {len(self.existing_jobs) + len(self.all_jobs)}")

        # Freshness breakdown for new jobs
        if self.all_jobs:
            high_pri = len([j for j in self.all_jobs if j.get('apply_priority') == 'HIGH'])
            print(f"\n🔥 Apply immediately:    {high_pri} HIGH priority jobs (<24h old)")

        print()

        # Count by company (top 10)
        if self.all_jobs:
            company_counts = {}
            for job in self.all_jobs:
                company = job.get("company", "Unknown")
                company_counts[company] = company_counts.get(company, 0) + 1

            print("Top Companies (New Jobs):")
            for i, (company, count) in enumerate(sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10], 1):
                print(f"  {i:2d}. {company:30s} {count:3d} jobs")

        print("=" * 70)

    def save_results(self):
        """Save all jobs to optimized structure."""
        if not self.all_jobs:
            print("\n⚠️  No new jobs to save!")
            return

        print(f"\n💾 Saving {len(self.all_jobs)} new jobs...")
        today = datetime.now().strftime("%Y-%m-%d")

        # 1. Update master all_jobs.json (append new jobs)
        all_jobs_combined = self.existing_jobs + self.all_jobs
        master_json = self.output_dir / "all_jobs.json"
        with open(master_json, 'w') as f:
            json.dump(all_jobs_combined, f, indent=2)
        print(f"   ✅ Master JSON: {master_json} ({len(all_jobs_combined)} total jobs)")

        # 2. Save today's scrape as daily snapshot
        daily_file = self.output_dir / "daily" / f"{today}.json"
        with open(daily_file, 'w') as f:
            json.dump(self.all_jobs, f, indent=2)
        print(f"   ✅ Daily snapshot: {daily_file}")

        # 3. Save by company
        jobs_by_company = {}
        for job in self.all_jobs:
            company = job.get("company", "Unknown").lower().replace(" ", "_")
            if company not in jobs_by_company:
                jobs_by_company[company] = []
            jobs_by_company[company].append(job)

        for company, jobs in jobs_by_company.items():
            company_file = self.output_dir / "by_company" / f"{company}.json"

            # Load existing company jobs if file exists
            existing_company_jobs = []
            if company_file.exists():
                try:
                    with open(company_file, 'r') as f:
                        existing_company_jobs = json.load(f)
                except:
                    pass

            # Append new jobs
            all_company_jobs = existing_company_jobs + jobs

            with open(company_file, 'w') as f:
                json.dump(all_company_jobs, f, indent=2)

        print(f"   ✅ Updated {len(jobs_by_company)} company files")

        # 4. Update summary CSV with freshness data
        csv_path = self.output_dir / "jobs_summary.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'apply_priority', 'hours_old', 'freshness_score', 'company', 'title',
                'location', 'portal', 'first_discovered', 'url'
            ])
            writer.writeheader()
            # Sort by freshness_score descending (freshest first)
            sorted_jobs = sorted(all_jobs_combined, key=lambda x: x.get('freshness_score', 0), reverse=True)
            for job in sorted_jobs:
                writer.writerow({
                    'apply_priority': job.get('apply_priority', 'UNKNOWN'),
                    'hours_old': job.get('hours_old', ''),
                    'freshness_score': job.get('freshness_score', ''),
                    'company': job.get('company'),
                    'title': job.get('title'),
                    'location': job.get('location'),
                    'portal': job.get('portal'),
                    'first_discovered': job.get('first_discovered', '')[:10] if job.get('first_discovered') else '',
                    'url': job.get('url')
                })
        print(f"   ✅ CSV summary: {csv_path} ({len(all_jobs_combined)} rows, sorted by freshness)")

        # 5. Create README in jobs folder with freshness stats
        readme_path = self.output_dir / "README.md"

        # Calculate freshness stats
        high_pri = len([j for j in all_jobs_combined if j.get('apply_priority') == 'HIGH'])
        med_pri = len([j for j in all_jobs_combined if j.get('apply_priority') == 'MEDIUM'])
        low_pri = len([j for j in all_jobs_combined if j.get('apply_priority') == 'LOW'])

        with open(readme_path, 'w') as f:
            f.write(f"""# Job Scraping Results

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## 📊 Stats

- **Total Unique Jobs:** {len(all_jobs_combined)}
- **New Jobs This Run:** {len(self.all_jobs)}
- **Companies Tracked:** {len(jobs_by_company)}

## 🔥 Freshness Breakdown (Apply Priority)

- **HIGH (<24h):** {high_pri} jobs 🎯 **APPLY NOW!**
- **MEDIUM (24-48h):** {med_pri} jobs ⚡ Apply today
- **LOW (2-7 days):** {low_pri} jobs 📋 Lower priority

**Goal:** Apply within 24 hours of posting for best chance!

## 📁 File Structure

- `jobs_summary.csv` - **START HERE** (sorted by freshness, Excel-friendly)
- `all_jobs.json` - All unique jobs (deduplicated, with full JD)
- `daily/YYYY-MM-DD.json` - Jobs scraped each day
- `by_company/company.json` - Jobs grouped by company

## 🎯 How to Use

1. **Open `jobs_summary.csv`** in Excel/Google Sheets
2. **Filter by `apply_priority = HIGH`** (jobs < 24h old)
3. **Sort by `freshness_score`** (100 = just posted)
4. **Apply to HIGH priority jobs first!**

## 📋 CSV Columns Explained

- `apply_priority`: HIGH (<24h), MEDIUM (24-48h), LOW (2-7d), EXPIRED (>7d)
- `hours_old`: How many hours since WE first discovered it
- `freshness_score`: 0-100 (100 = just posted, apply immediately!)
- `first_discovered`: When our scraper first saw this job (proxy for posting date)

## 🔍 Detailed Job Data

For full job descriptions and metadata:
1. `all_jobs.json` - Complete data with JD, departments, etc.
2. `by_company/company.json` - All jobs from specific company
3. `daily/` - Historical snapshots

## ⚡ Pro Tip

With hourly scraping, `first_discovered` ≈ posting time (±1 hour).
Focus on jobs with `hours_old < 24` for best application success rate!
""")
        print(f"   ✅ README: {readme_path}")

        print(f"\n✅ SCRAPING COMPLETE!")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        print(f"🎯 Total jobs in database: {len(all_jobs_combined)}")
        print(f"🆕 New jobs this run: {len(self.all_jobs)}")


def main():
    """Main entry point."""
    scraper = ProductionScraperV3()
    scraper.scrape_all()


if __name__ == "__main__":
    main()
