import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

def get_dynamic_skills(text):
    """
    Manually extracts meaningful keywords from any text (JD or Resume) 
    without using a predefined JSON list.
    """
    if not text:
        return set()
    # Clean and tokenize
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    tokens = word_tokenize(text)
    # Filter for meaningful technical/professional words
    # You can add a custom logic here to keep words like 'python', 'react' 
    keywords = {w for w in tokens if w not in stop_words and len(w) > 1}
    return keywords

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

    score = int((len(matched) / len(jd_skills)) * 100) if jd_skills else 0
    return score, matched, missing[:15] # Limit missing to top 15