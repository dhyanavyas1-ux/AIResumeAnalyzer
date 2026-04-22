"""
suggestions.py
==============
AI Suggestions Engine for the Resume Analyzer.

Generates dynamic, context-aware, actionable recommendations
based on the analysis results:
  - Match score band
  - Missing skills
  - Grammar issues
  - Experience and education detection

Each suggestion is a dict:
  {
    'icon':     str  (emoji icon for the UI),
    'priority': str  ('High' | 'Medium' | 'Low'),
    'title':    str  (short headline),
    'message':  str  (detailed actionable advice),
  }
"""

import re


# ── Priority colour mapping (used in template rendering) ─────────────────────
PRIORITY_COLOURS = {
    'High':   '#ef4444',   # red
    'Medium': '#f59e0b',   # amber
    'Low':    '#10b981',   # green
}


def generate_suggestions(
    score: int,
    missing_skills: list[str],
    grammar_issues: list[dict],
    resume_text: str = '',
) -> list[dict]:
    """
    Generate a list of personalised improvement suggestions.

    Args:
        score          : Final match score (0-100).
        missing_skills : List of skill keywords absent from the resume.
        grammar_issues : List of grammar issue dicts from nlp_engine.
        resume_text    : Raw resume text for deeper analysis.

    Returns:
        List of suggestion dicts (sorted: High → Medium → Low).
    """
    suggestions = []
    lower_text = resume_text.lower() if resume_text else ''

    # ── 1. Score-band general advice ─────────────────────────────────────────
    if score < 30:
        suggestions.append({
            'icon': '🎯',
            'priority': 'High',
            'title': 'Low Match Detected — Major Revision Needed',
            'message': (
                'Your resume matches fewer than 30% of the job requirements. '
                'Read the job description carefully and tailor your resume to '
                'reflect the exact technologies, tools, and responsibilities '
                'listed. Consider adding a dedicated "Skills" section.'
            ),
        })
    elif score < 55:
        suggestions.append({
            'icon': '✏️',
            'priority': 'High',
            'title': 'Moderate Match — Targeted Improvements Required',
            'message': (
                'You match about half the job requirements. Focus on adding the '
                'missing skills below either through projects, certifications, '
                'or by rewriting existing bullet points using exact JD keywords.'
            ),
        })
    elif score < 75:
        suggestions.append({
            'icon': '📈',
            'priority': 'Medium',
            'title': 'Good Match — Fine-Tune for Higher ATS Score',
            'message': (
                'Your resume is a solid match. Incorporate a few more keywords '
                'from the job description, especially in your summary and '
                'experience bullet points, to push the score above 80%.'
            ),
        })
    else:
        suggestions.append({
            'icon': '🏆',
            'priority': 'Low',
            'title': 'Excellent Match — Polish & Format',
            'message': (
                'Great job! Your resume aligns well with the role. Focus now on '
                'formatting: consistent fonts, clean section headers, and '
                'concise bullet points that start with strong action verbs.'
            ),
        })

    # ── 2. Missing skills suggestions ────────────────────────────────────────
    if missing_skills:
        top_missing = [s.title() for s in missing_skills[:6]]
        missing_str = ', '.join(top_missing)
        suggestions.append({
            'icon': '🛠️',
            'priority': 'High',
            'title': f'Add Missing Skills: {", ".join(top_missing[:3])}{"…" if len(top_missing) > 3 else ""}',
            'message': (
                f'The following keywords are in the job description but missing '
                f'from your resume: {missing_str}. '
                'Add them to your Skills section or weave them naturally into '
                'your project and experience descriptions.'
            ),
        })

    # ── 3. ATS keyword density suggestion ───────────────────────────────────
    if score < 70:
        suggestions.append({
            'icon': '🤖',
            'priority': 'Medium',
            'title': 'Improve ATS Keyword Density',
            'message': (
                'Applicant Tracking Systems (ATS) rank resumes by keyword '
                'frequency. Use the exact terms from the job description — '
                'e.g., if the JD says "React.js", use "React.js" not just '
                '"React". Avoid stylised fonts, tables, or images that ATS '
                'systems cannot parse.'
            ),
        })

    # ── 4. Grammar & spelling ────────────────────────────────────────────────
    if grammar_issues:
        suggestions.append({
            'icon': '📝',
            'priority': 'Medium',
            'title': f'{len(grammar_issues)} Grammar Issue(s) Detected',
            'message': (
                'Grammar errors reduce your professional credibility. Run your '
                'resume through Grammarly or Hemingway Editor. Pay special '
                'attention to subject-verb agreement, tense consistency '
                '(use past tense for previous roles), and article usage.'
            ),
        })

    # ── 5. Quantified achievements check ─────────────────────────────────────
    has_numbers = bool(re.search(r'\d+\s*(%|x|times|million|lakh|crore|users|clients|projects)', lower_text))
    if not has_numbers:
        suggestions.append({
            'icon': '📊',
            'priority': 'Medium',
            'title': 'Quantify Your Achievements',
            'message': (
                'Recruiters respond to numbers. Instead of "Improved system '
                'performance", write "Improved system performance by 40%, '
                'reducing load time from 3s to 1.8s." Add metrics, percentages, '
                'team sizes, or revenue impact wherever possible.'
            ),
        })

    # ── 6. Summary / Objective section ───────────────────────────────────────
    has_summary = any(kw in lower_text for kw in ['summary', 'objective', 'profile', 'about me'])
    if not has_summary:
        suggestions.append({
            'icon': '📄',
            'priority': 'Medium',
            'title': 'Add a Professional Summary',
            'message': (
                'A 3-4 line professional summary at the top of your resume '
                'dramatically improves ATS scoring and recruiter engagement. '
                'Include your years of experience, top 2-3 skills, and the '
                'specific role you are targeting.'
            ),
        })

    # ── 7. Project section check ─────────────────────────────────────────────
    has_projects = any(kw in lower_text for kw in ['project', 'built', 'developed', 'created', 'deployed'])
    if not has_projects:
        suggestions.append({
            'icon': '🚀',
            'priority': 'Low',
            'title': 'Showcase Personal or Academic Projects',
            'message': (
                'Add a Projects section listing 2-3 relevant projects with: '
                'project name, technologies used, your role, and measurable '
                'outcomes. GitHub links or live demos significantly boost credibility.'
            ),
        })

    # ── 8. LinkedIn / GitHub / Portfolio ─────────────────────────────────────
    has_links = any(kw in lower_text for kw in ['linkedin', 'github', 'portfolio', 'behance', 'dribbble'])
    if not has_links:
        suggestions.append({
            'icon': '🔗',
            'priority': 'Low',
            'title': 'Add Professional Profile Links',
            'message': (
                'Include your LinkedIn profile URL, GitHub profile (for tech roles), '
                'or portfolio website in the header of your resume. '
                'Many modern ATS systems parse these links automatically.'
            ),
        })

    # ── Sort: High first, then Medium, then Low ───────────────────────────────
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    suggestions.sort(key=lambda s: priority_order.get(s['priority'], 3))

    return suggestions
