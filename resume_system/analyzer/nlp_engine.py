"""
nlp_engine.py
=============
NLP processing utilities for the AI Resume Analyzer.

This module provides:
  - clean_universal_text()        → tokenize & extract meaningful nouns from any text
  - detect_grammar_errors()       → rule-based grammar issue detection
  - detect_spelling_errors()      → basic spell-check returning (wrong, suggestion) pairs
  - ai_grammar_integrity_check()  → combined grammar score + corrected text
  - ai_tone_authenticity_check()  → tone & authenticity scoring
  - ai_content_likelihood()       → likelihood that resume content is AI-generated (0-100)
"""

import re
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# ── Ensure required NLTK data is downloaded ──────────────────────────────────
for resource, path in [
    ('punkt_tab', 'tokenizers/punkt_tab'),
    ('averaged_perceptron_tagger_eng', 'taggers/averaged_perceptron_tagger_eng'),
    ('stopwords', 'corpora/stopwords'),
]:
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(resource, quiet=True)


# ── 1. Core NLP: Extract keywords from raw text ──────────────────────────────

# Add this import at the very top of nlp_engine.py
from .skill_matcher import get_dynamic_skills

def clean_universal_text(text: str) -> list[str]:
    """
    Extracts valid technical skills and keywords from text 
    by cross-referencing with the predefined skills.json taxonomy.
    """
    if not text or not text.strip():
        return []
        
    # Delegate the work to your robust, multi-word capable JSON matcher
    extracted_skills_set = get_dynamic_skills(text)
    
    # Convert the set back to a list and capitalize the first letter 
    # so they look great on the frontend UI pills (e.g., "Python", "React")
    formatted_skills = [skill.title() for skill in extracted_skills_set]
    
    return formatted_skills


# ── 2. Grammar error detection ───────────────────────────────────────────────

# Common rule-based grammar patterns
_GRAMMAR_RULES = [
    # Subject-verb agreement
    (r'\bI has\b',          'Subject-verb agreement error',   'Use "I have" instead of "I has".'),
    (r'\bhe have\b',        'Subject-verb agreement error',   'Use "he has" instead of "he have".'),
    (r'\bshe have\b',       'Subject-verb agreement error',   'Use "she has" instead of "she have".'),
    (r'\bthey has\b',       'Subject-verb agreement error',   'Use "they have" instead of "they has".'),
    # Article misuse
    (r'\ba [aeiou]',        'Article use error',              'Use "an" before vowel sounds (e.g., "an engineer", not "a engineer").'),
    # Tense inconsistency (past + present in same text)
]

def detect_grammar_errors(text: str) -> list[dict]:
    """
    Scan text for common grammar issues using regex rules.

    Returns a list of dicts: {'message': str, 'suggestion': str}
    """
    if not text:
        return []

    issues = []
    lower_text = text.lower()

    for pattern, message, suggestion in _GRAMMAR_RULES:
        if re.search(pattern, lower_text):
            issues.append({'message': message, 'suggestion': suggestion})

    # Tense inconsistency check
    if re.search(r'\bworked\b', lower_text) and re.search(r'\bworks\b', lower_text):
        issues.append({
            'message': 'Inconsistent tense detected',
            'suggestion': 'Use past tense ("worked") consistently for previous roles.'
        })

    return issues


# ── 3. Spelling error detection ───────────────────────────────────────────────

# Curated dictionary of common resume misspellings → correct word
_COMMON_MISSPELLINGS = {
    'pyhton': 'Python',
    'pyhon': 'Python',
    'pytohn': 'Python',
    'experiance': 'experience',
    'expirence': 'experience',
    'managment': 'management',
    'develpment': 'development',
    'developement': 'development',
    'implmentation': 'implementation',
    'implimentation': 'implementation',
    'comunication': 'communication',
    'programing': 'programming',
    'algortihm': 'algorithm',
    'databse': 'database',
    'knowldge': 'knowledge',
    'achived': 'achieved',
    'acheived': 'achieved',
    'teh': 'the',
    'recieve': 'receive',
    'sucessful': 'successful',
}

def detect_spelling_errors(text: str) -> list[tuple[str, str]]:
    """
    Check text for known resume misspellings.

    Returns a list of (wrong_word, correct_suggestion) tuples.
    """
    if not text:
        return []

    errors = []
    tokens = re.findall(r'\b\w+\b', text.lower())
    seen = set()

    for token in tokens:
        if token in _COMMON_MISSPELLINGS and token not in seen:
            errors.append((token, _COMMON_MISSPELLINGS[token]))
            seen.add(token)

    return errors


# ── 4. AI Grammar Integrity Check ────────────────────────────────────────────

def ai_grammar_integrity_check(text: str) -> dict:
    """
    Perform a heuristic grammar integrity check on the given text.

    Scoring:
      - Starts at 100
      - Deducts 10 per grammar issue found
      - Deducts 5  per spelling error found
      - 'integrity_score': reflects overall textual consistency (1 if OK, 0 if issues found)
      - 'corrected_text': applies known spelling corrections

    Returns:
        {
          'grammar_score': int (0-100),
          'integrity_score': int (0 or 1),
          'review': str,
          'corrected_text': str,
        }
    """
    grammar_issues = detect_grammar_errors(text)
    spelling_errors = detect_spelling_errors(text)

    # Build corrected text by substituting known misspellings
    corrected = text
    for wrong, right in spelling_errors:
        corrected = re.sub(r'\b' + re.escape(wrong) + r'\b', right, corrected, flags=re.IGNORECASE)

    # Also fix known grammar patterns
    corrected = re.sub(r'\bI has\b', 'I have', corrected, flags=re.IGNORECASE)

    score = max(0, 100 - len(grammar_issues) * 10 - len(spelling_errors) * 5)
    integrity = 0 if (grammar_issues or spelling_errors) else 1

    if score >= 90:
        review = "Excellent grammar and spelling. Your resume text reads professionally."
    elif score >= 70:
        review = "Good grammar overall with a few minor issues. Consider reviewing before submission."
    elif score >= 50:
        review = "Several grammar or spelling issues detected. Proofread carefully."
    else:
        review = "Significant grammar/spelling issues found. Consider using a grammar checker tool."

    return {
        'grammar_score': score,
        'integrity_score': integrity,
        'review': review,
        'corrected_text': corrected,
    }


# ── 5. Tone & Authenticity Check ─────────────────────────────────────────────

# Power verbs signal active, results-driven writing
_POWER_VERBS = [
    'led', 'built', 'created', 'designed', 'developed', 'launched', 'managed',
    'achieved', 'delivered', 'improved', 'optimized', 'reduced', 'increased',
    'implemented', 'spearheaded', 'coordinated', 'mentored', 'automated',
    'deployed', 'architected', 'scaled', 'drove', 'established',
]

# Weak or vague words that hurt authenticity
_WEAK_WORDS = [
    'helped', 'assisted', 'worked on', 'participated', 'was responsible for',
    'tried', 'attempted', 'sort of', 'basically', 'various', 'several',
]

def ai_tone_authenticity_check(text: str) -> dict:
    """
    Evaluate the tone and authenticity of resume text.

    - tone_score      : how action-oriented and professional the language is (0-100)
    - authenticity_score : how specific and non-generic the writing feels (0-100)

    Returns:
        {
          'tone_score': int,
          'authenticity_score': int,
          'review': str,
        }
    """
    if not text:
        return {'tone_score': 0, 'authenticity_score': 0, 'review': 'No text provided.'}

    lower = text.lower()
    words = re.findall(r'\b\w+\b', lower)
    total_words = max(len(words), 1)

    # Count power verbs found
    power_count = sum(1 for v in _POWER_VERBS if v in lower)
    # Count weak words found
    weak_count = sum(1 for w in _WEAK_WORDS if w in lower)

    # Tone: reward power verbs, penalise weak words
    tone_score = min(100, max(0, 50 + power_count * 8 - weak_count * 10))

    # Authenticity: penalise extreme adjective overuse ("awesome", "best", "amazing")
    hype_words = ['awesome', 'amazing', 'best', 'excellent', 'outstanding', 'exceptional', 'perfect']
    hype_count = sum(1 for h in hype_words if h in lower)
    authenticity_score = min(100, max(0, 80 - hype_count * 15))

    # Combined review
    avg = (tone_score + authenticity_score) // 2
    if avg >= 75:
        review = "Strong, professional tone with clear action-oriented language."
    elif avg >= 50:
        review = "Decent tone. Add more power verbs and quantify achievements."
    else:
        review = "Weak or vague language detected. Replace passive phrases with strong action verbs."

    return {
        'tone_score': tone_score,
        'authenticity_score': authenticity_score,
        'review': review,
    }


# ── 6. AI Content Likelihood ─────────────────────────────────────────────────

# Phrases strongly associated with AI-generated content
_AI_SIGNAL_PHRASES = [
    'as an ai', 'as a language model', 'chatgpt', 'openai', 'llm',
    'i am an artificial intelligence', 'i cannot', 'i apologize',
    'certainly!', 'of course!', 'absolutely!', 'delve', 'leverage synergies',
    'paradigm shift', 'holistic approach', 'proactive synergy', 'game-changing',
    'revolutionary', 'cutting-edge solutions', 'seamlessly integrates',
]

def ai_content_likelihood(text: str) -> int:
    """
    Estimate the probability (0–100) that the resume text was generated by an AI.

    Uses a simple signal-phrase count heuristic. Higher score = more likely AI-written.

    Args:
        text: Resume text string.

    Returns:
        int — AI content likelihood score (0-100).
    """
    if not text:
        return 0

    lower = text.lower()
    hit_count = sum(1 for phrase in _AI_SIGNAL_PHRASES if phrase in lower)

    # Each hit contributes ~15 points, capped at 100
    score = min(100, hit_count * 15)
    return score