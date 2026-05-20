import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APP_ID  = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search"

JOB_TITLES = [
    "data analyst",
    "data scientist",
    "business intelligence analyst",
    "machine learning engineer",
    "analytics engineer",
    "financial analyst",
    "business analyst",
    "risk analyst",
    "quantitative analyst",
    "product analyst",
    "data engineer",
]

CATEGORIES = [
    "finance-jobs",
    "it-jobs",
    "accounting-finance-jobs",
]

def fetch_jobs(job_title, category, pages=3):
    jobs = []
    for page in range(1, pages + 1):
        params = {
            "app_id":          APP_ID,
            "app_key":         APP_KEY,
            "what":            job_title,
            "category":        category,
            "results_per_page": 50,
            "content-type":    "application/json",
        }
        response = requests.get(f"{BASE_URL}/{page}", params=params)
        if response.status_code != 200:
            print(f"Error fetching {job_title} / {category}: {response.status_code}")
            continue

        data = response.json()
        for job in data.get("results", []):
            jobs.append({
                "title":       job.get("title"),
                "company":     job.get("company", {}).get("display_name"),
                "location":    job.get("location", {}).get("display_name"),
                "category":    job.get("category", {}).get("label"),
                "salary_min":  job.get("salary_min"),
                "salary_max":  job.get("salary_max"),
                "description": job.get("description"),
                "created":     job.get("created"),
                "search_term": job_title,
            })
        print(f"Fetched page {page} for '{job_title}' in '{category}'")

    return jobs


def collect_all():
    all_jobs = []
    for title in JOB_TITLES:
        for category in CATEGORIES:
            jobs = fetch_jobs(title, category)
            all_jobs.extend(jobs)

    df = pd.DataFrame(all_jobs)
    df["created"] = pd.to_datetime(df["created"], errors="coerce")
    df["collected_at"] = datetime.now()
    df = df.drop_duplicates(subset=["title", "company", "location", "created"])

    os.makedirs("data", exist_ok=True)
    output_path = "data/jobs_data.csv"
    df.to_csv(output_path, index=False)
    print(f"\nDone. {len(df)} jobs saved to {output_path}")
    return df


if __name__ == "__main__":
    collect_all()
