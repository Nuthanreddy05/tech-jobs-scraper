# 🚀 GitHub Actions Career Page Scraper

**Scrapes 100+ software/data jobs from top tech company career pages** - runs entirely in GitHub's cloud, bypassing all network restrictions!

## ✨ Features

- ✅ Scrapes from **Amazon, Google, Microsoft, Meta, Apple**, and more
- ✅ Runs **automatically** every day via GitHub Actions
- ✅ **FREE** (runs in GitHub's cloud)
- ✅ AI-powered parsing with Groq
- ✅ Filters for **software/data roles** + **US locations**
- ✅ Saves results as JSON + individual folders

## 🎯 Based on Research

This project is inspired by:
- [JobSpy](https://github.com/speedyapply/JobSpy) - Job scraping library
- [Automated Job Web Scraping](https://github.com/anthonyjdella/automated-job-web-scraping)
- [GitHub Actions for Scraping](https://medium.com/@lassebenninga/setup-free-webscraping-in-less-than-5-minutes-using-github-actions-330e1151fbea)

## 🛠️ Setup Instructions

### 1. Create GitHub Repository

```bash
# On your computer (not in VM)
cd ~/Desktop
mkdir tech-jobs-scraper
cd tech-jobs-scraper
git init
git remote add origin https://github.com/YOUR_USERNAME/tech-jobs-scraper.git
```

### 2. Copy Files

Copy these files to your new repo:
- `.github/workflows/scrape_jobs.yml`
- `scraper.py`
- `requirements.txt`
- `README.md`

### 3. Add Groq API Key (Optional but Recommended)

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GROQ_API_KEY`
4. Value: `YOUR_GROQ_API_KEY_HERE`

### 4. Push to GitHub

```bash
git add .
git commit -m "Initial commit: Career page scraper"
git push -u origin main
```

### 5. Enable GitHub Actions

1. Go to your repo on GitHub
2. Click **Actions** tab
3. Click **"I understand my workflows, go ahead and enable them"**

### 6. Run Manually (First Time)

1. Go to **Actions** tab
2. Select **"Scrape Tech Jobs from Career Pages"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait 5-10 minutes
5. Check the `jobs/` folder for results!

## 📊 Results

After running, you'll get:
- `jobs/all_jobs.json` - All jobs in one file
- `jobs/job_001/`, `jobs/job_002/`, etc. - Individual job folders
- Each folder has `details.json` and `apply_url.txt`

## 🔄 Automatic Daily Runs

The workflow runs **automatically every day at 9 AM UTC**. Results are committed to your repo automatically.

## 🎨 Customize Companies

Edit `scraper.py` line 97 to add/remove companies:

```python
companies = [
    {"name": "YourCompany", "url": "https://careers.yourcompany.com/jobs"},
    # Add more...
]
```

## 📈 Scaling Up

To scrape more companies:
1. Add them to the `companies` list
2. Increase delay between requests (line 115): `time.sleep(10)`
3. Consider using [proxy services](https://www.kdnuggets.com/2025/11/brightdata/the-best-proxy-providers-for-large-scale-scraping-for-2026) for large-scale scraping

## 🔥 Why This Works

- **GitHub Actions** provides fresh VMs with full internet access
- **No network restrictions** (unlike your local VM)
- **Free** for public repos (2,000 minutes/month)
- **Automated** - set and forget

## 📚 Sources

- [Best Proxy Providers for Scraping 2026](https://www.kdnuggets.com/2025/11/brightdata/the-best-proxy-providers-for-large-scale-scraping-for-2026)
- [GitHub Actions Scraping Guide](https://www.swyx.io/github-scraping)
- [Career Crawler GitHub](https://github.com/amrrdev/career-crawler)
- [JobSpy Library](https://github.com/speedyapply/JobSpy)
- [Serverless Scraping Service](https://github.com/data-for-good-concepts/serverless-scraping-service)

## 🤝 Contributing

Feel free to add more companies, improve parsers, or enhance filtering!

## ⚠️ Legal Note

Always respect `robots.txt` and terms of service. This tool is for personal job search only.
