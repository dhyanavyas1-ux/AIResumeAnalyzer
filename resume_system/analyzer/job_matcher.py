"""
job_matcher.py
==============
Fetches real-time job listings from the JSearch API (RapidAPI).

Primary:  JSearch API  — live results
Fallback: Static curated jobs — shown when API key is missing or request fails

Usage:
    from analyzer.job_matcher import get_real_time_jobs
    jobs = get_real_time_jobs("Python Django developer jobs in India")
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
# Set your RapidAPI key in an environment variable: RAPIDAPI_KEY
# Or replace the empty string below with your key directly (not recommended for production).
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', 'YOUR_API_KEY_HERE')

JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"
JSEARCH_HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}

# ── Static fallback jobs (shown when API unavailable) ─────────────────────────
STATIC_JOBS = [
    {
        'title': 'Python Backend Developer',
        'company': 'TCS',
        'location': 'Bengaluru',
        'link': 'https://ibegin.tcs.com/iBegin/',
        'salary': '₹6–12 LPA',
    },
    {
        'title': 'Data Scientist',
        'company': 'Infosys',
        'location': 'Hyderabad',
        'link': 'https://career.infosys.com/',
        'salary': '₹8–16 LPA',
    },
    {
        'title': 'Frontend Developer',
        'company': 'Wipro',
        'location': 'Pune',
        'link': 'https://careers.wipro.com/',
        'salary': '₹5–10 LPA',
    },
    {
        'title': 'Full Stack Developer',
        'company': 'HCL Technologies',
        'location': 'Noida',
        'link': 'https://www.hcltech.com/careers',
        'salary': '₹7–14 LPA',
    },
    {
        'title': 'Machine Learning Engineer',
        'company': 'Accenture',
        'location': 'Bengaluru',
        'link': 'https://www.accenture.com/in-en/careers',
        'salary': '₹10–20 LPA',
    },
    {
        'title': 'DevOps Engineer',
        'company': 'Tech Mahindra',
        'location': 'Bengaluru',
        'link': 'https://careers.techmahindra.com/',
        'salary': '₹8–15 LPA',
    },
    {
        'title': 'Data Analyst',
        'company': 'Capgemini',
        'location': 'Mumbai',
        'link': 'https://www.capgemini.com/in-en/careers/',
        'salary': '₹5–9 LPA',
    },
    {
        'title': 'Java Developer',
        'company': 'Cognizant',
        'location': 'Chennai',
        'link': 'https://careers.cognizant.com/',
        'salary': '₹6–13 LPA',
    },
]


def get_real_time_jobs(skills_query: str | list, num_results: int = 5) -> list[dict]:
    """
    Fetch job listings using the JSearch RapidAPI.

    Args:
        skills_query : Either a search string or a list of skill strings.
                       If a list, the first 3 items are joined + " jobs in India".
        num_results  : Maximum number of job listings to return.

    Returns:
        List of dicts: {'title', 'company', 'location', 'link', 'salary'}
        Falls back to STATIC_JOBS[:num_results] if API call fails.
    """
    # ── Build the query string ─────────────────────────────────────────────
    if isinstance(skills_query, list):
        query = f"{' '.join(skills_query[:3])} developer jobs in India"
    else:
        query = skills_query or "Junior Developer jobs in India"

    # ── Skip live API if key is placeholder ───────────────────────────────
    if not RAPIDAPI_KEY or RAPIDAPI_KEY == 'YOUR_API_KEY_HERE':
        return STATIC_JOBS[:num_results]

    # ── Live API call ──────────────────────────────────────────────────────
    try:
        response = requests.get(
            JSEARCH_URL,
            headers=JSEARCH_HEADERS,
            params={"query": query, "num_pages": "1", "page": "1"},
            timeout=8,
        )
        response.raise_for_status()
        data = response.json().get('data', [])

        if not data:
            return STATIC_JOBS[:num_results]

        jobs = []
        for j in data[:num_results]:
            jobs.append({
                'title':    j.get('job_title', 'Untitled Role'),
                'company':  j.get('employer_name', 'Unknown Company'),
                'location': j.get('job_city') or j.get('job_country', 'India'),
                'link':     j.get('job_apply_link', '#'),
                'salary':   _format_salary(j),
            })
        return jobs

    except Exception as exc:
        # Log to console but don't crash the page
        print(f"[JSearch API] Failed: {exc}. Falling back to static jobs.")
        return STATIC_JOBS[:num_results]


def _format_salary(job: dict) -> str:
    """Extract and format salary info from a JSearch job record."""
    min_sal = job.get('job_min_salary')
    max_sal = job.get('job_max_salary')
    currency = job.get('job_salary_currency', '')

    if min_sal and max_sal:
        return f"{currency} {int(min_sal):,} – {int(max_sal):,}"
    elif min_sal:
        return f"{currency} {int(min_sal):,}+"
    return "Salary not disclosed"