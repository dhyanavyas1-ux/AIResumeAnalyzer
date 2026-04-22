import re
import json
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

# 1. Load your skills.json globally so it only reads the file once when the server starts
# This builds the correct path assuming skill_matcher.py is in analyzer/ and skills.json is in data/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_FILE_PATH = os.path.join(BASE_DIR, 'data', 'skills.json')

try:
    with open(SKILLS_FILE_PATH, 'r', encoding='utf-8') as f:
        skills_data = json.load(f)
        # Convert the list to a set for lightning-fast lookups
        VALID_SKILLS = set([skill.lower() for skill in skills_data.get('skills', [])])
except FileNotFoundError:
    VALID_SKILLS = set()
    print("Warning: skills.json not found at", SKILLS_FILE_PATH)

def get_dynamic_skills(text):
    """
    Extracts meaningful keywords from text by strictly matching against skills.json.
    Supports both single-word and multi-word skills.
    """
    if not text:
        return set()
    
    text_lower = text.lower()
    found_skills = set()
    
    # 2. Iterate through your valid skills and search the text
    for skill in VALID_SKILLS:
        # Use regex word boundaries (\b) so a skill like "c" doesn't trigger inside the word "react"
        pattern = r'\b' + re.escape(skill) + r'\b'
        
        if re.search(pattern, text_lower):
            found_skills.add(skill)
            
    return found_skills

def skill_match(resume_text, job_description):
    """
    Performs manual matching between the Resume and the Job Description.
    """
    resume_skills = get_dynamic_skills(resume_text)
    jd_skills = get_dynamic_skills(job_description)
    
    # Manual Intersection: Only what is in both
    matched = list(resume_skills.intersection(jd_skills))
    
    # Manual Difference: What is in JD but NOT in Resume
    missing = list(jd_skills.difference(resume_skills))
    
    # Calculate score safely
    score = int((len(matched) / len(jd_skills)) * 100) if jd_skills else 0
    
    return score, matched, missing[:15] # Limit missing to top 15