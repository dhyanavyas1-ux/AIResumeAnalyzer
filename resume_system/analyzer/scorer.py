def final_score(skill_score, experience, education, projects):
    """
    Calculate final resume match score as a percentage (0-100).
    
    Weighting:
    - Skills: 50%
    - Experience (2+ years): 15%
    - Education: 15%
    - Projects: 20%
    """
    
    score = 0
    
    # 50% weight → skills (skill_score is already 0-100)
    score += (skill_score / 100) * 50
    
    # 15% weight → Experience
    if experience >= 2:
        score += 15
    elif experience >= 1:
        score += 7.5  # Partial credit for 1 year
    
    # 15% weight → Education
    if education:
        score += 15
    
    # 20% weight → Projects
    if projects:
        score += 20
    
    # Ensure score is between 0-100
    return min(100, max(0, int(score)))