import re
import json
from collections import Counter
import PyPDF2
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


STOP_WORDS = set(stopwords.words('english'))


# -----------------------------
# Extract text from PDF
# -----------------------------

def extract_text(pdf_path):

    text = ""

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            text += page.extract_text()

    return text


# -----------------------------
# Clean text
# -----------------------------

def clean_text(text):

    tokens = word_tokenize(text.lower())

    words = [
        w for w in tokens
        if w.isalpha() and w not in STOP_WORDS
    ]

    return words


# -----------------------------
# Load skills dataset
# -----------------------------

def load_skills():

    with open("data/skills.json") as f:
        skills = json.load(f)

    return skills["skills"]


# -----------------------------
# Extract skills
# -----------------------------

def extract_skills(words):

    skill_set = load_skills()

    found = []

    for word in words:
        if word in skill_set:
            found.append(word)

    return list(set(found))


# -----------------------------
# Experience detection
# -----------------------------

def detect_experience(text):

    match = re.search(r'(\d+)\s+(year|years)', text.lower())

    if match:
        return int(match.group(1))

    return 0


# -----------------------------
# Education detection
# -----------------------------

EDUCATION = [
    "b.tech",
    "bachelor",
    "bsc",
    "computer science",
    "information technology"
]


def detect_education(text):

    text = text.lower()

    for word in EDUCATION:
        if word in text:
            return True

    return False


# -----------------------------
# Project detection
# -----------------------------

PROJECT_KEYWORDS = [
    "project",
    "developed",
    "implemented",
    "designed"
]


def detect_projects(text):

    text = text.lower()

    for word in PROJECT_KEYWORDS:
        if word in text:
            return True

    return False


# -----------------------------
# Keyword density
# -----------------------------

def keyword_density(text, skills):

    text = text.lower()

    density = {}

    for skill in skills:
        density[skill] = text.count(skill)

    return density


# -----------------------------
# Job role skills
# -----------------------------

JOB_ROLE_SKILLS = {
    "python backend developer": ["python","django","sql","rest"],
    "data scientist": ["python","pandas","numpy","machine learning"],
    "frontend developer": ["html","css","javascript","react"]
}


# -----------------------------
# Skill match score
# -----------------------------

def skill_match(resume_skills, role):

    role = role.lower()

    required = JOB_ROLE_SKILLS.get(role, [])

    if not required:
        return 0, []

    matched = set(resume_skills) & set(required)

    missing = list(set(required) - set(resume_skills))

    score = int((len(matched) / len(required)) * 100)

    return score, missing


# -----------------------------
# Final score
# -----------------------------

def final_score(skill_score, experience, education, projects):

    score = 0

    score += skill_score * 0.5

    if experience >= 2:
        score += 20

    if education:
        score += 15

    if projects:
        score += 15

    return int(score)


# -----------------------------
# Recommend jobs
# -----------------------------

def recommend_jobs(resume_skills):

    with open("data/jobs.json") as f:
        jobs = json.load(f)

    recommended = []

    for job in jobs:

        matched = set(resume_skills) & set(job["skills"])

        score = int((len(matched) / len(job["skills"])) * 100)

        recommended.append({
            "title": job["title"],
            "score": score,
            "apply_link": job["apply_link"]
        })

    recommended.sort(key=lambda x: x["score"], reverse=True)

    return recommended[:3]