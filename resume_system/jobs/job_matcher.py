import json
from .job_loader import load_jobs

def recommend_jobs(resume_skills):
    jobs = load_jobs()
    recommendations = []

    for job in jobs:
        matched = set(resume_skills) & set(job['skills'])
        score = int((len(matched) / len(job['skills'])) * 100)

        if score > 40:
            job['match'] = score
            recommendations.append(job)

    return sorted(recommendations, key=lambda x: x['match'], reverse=True)