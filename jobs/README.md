# Job Scraping Results

**Last Updated:** 2026-02-07 14:39:53 UTC

## 📊 Stats

- **Total Unique Jobs:** 3825
- **New Jobs This Run:** 1
- **Companies Tracked:** 1

## 🔥 Freshness Breakdown (Apply Priority)

- **HIGH (<24h):** 1392 jobs 🎯 **APPLY NOW!**
- **MEDIUM (24-48h):** 0 jobs ⚡ Apply today
- **LOW (2-7 days):** 0 jobs 📋 Lower priority

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
