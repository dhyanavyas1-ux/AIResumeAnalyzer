from django.test import TestCase

from analyzer.nlp_engine import ai_grammar_integrity_check, ai_tone_authenticity_check, detect_spelling_errors, detect_grammar_errors, ai_content_likelihood
from analyzer.skill_matcher import get_dynamic_skills, skill_match 


class NLPEngineTests(TestCase):
    def test_ai_grammar_integrity_check_short_text(self):
        r = ai_grammar_integrity_check('Too short')
        self.assertIn('grammar_score', r)
        self.assertIn('integrity_score', r)
        self.assertIn('review', r)

    def test_ai_tone_authenticity_check(self):
        r = ai_tone_authenticity_check('I led development of an awesome feature and achieved results.')
        self.assertIn('tone_score', r)
        self.assertIn('authenticity_score', r)
        self.assertIn('review', r)

    def test_detect_spelling_errors(self):
        errs = detect_spelling_errors('I have teh best experiance ever.')
        self.assertTrue(any(item[0].lower() in ['teh', 'experiance'] for item in errs))

    def test_detect_grammar_errors(self):
        errors = detect_grammar_errors('I has a experience in software development.')
        self.assertIsInstance(errors, list)
        # if language_tool_python is not installed, just ensure no crash

    def test_detect_grammar_errors_fallback(self):
        errors = detect_grammar_errors('I has a experience in software development.')
        self.assertTrue(any('Subject-verb agreement' in e['message'] or 'Article use' in e['message'] for e in errors))

    def test_ai_grammar_integrity_correction(self):
        text = 'I has a experience in software development with teh best outcomes.'
        result = ai_grammar_integrity_check(text)
        self.assertIn('corrected_text', result)
        self.assertIn('I have', result['corrected_text'])
        self.assertIn('the best', result['corrected_text'])

    def test_ai_content_likelihood(self):
        score = ai_content_likelihood('This resume mentions AI, ChatGPT and OpenAI many times.')
        self.assertGreaterEqual(score, 20)

class SkillMatcherTests(TestCase):

    def test_get_dynamic_skills_filtering(self):
        """Test that it filters out basic words and keeps actual skills based on skills.json"""
        text = "I have the ability to build applications using Python, Django, and SQL."
        skills = get_dynamic_skills(text)
        
        # These should be found
        self.assertIn('python', skills)
        self.assertIn('django', skills)
        self.assertIn('sql', skills)
        
        # These generic nouns should NOT be found anymore!
        self.assertNotIn('ability', skills)
        self.assertNotIn('applications', skills)

    def test_get_dynamic_skills_multi_word(self):
        """Test that multi-word skills are detected correctly without splitting"""
        text = "Experience with Machine Learning, Data Structures, and React."
        skills = get_dynamic_skills(text)
        
        self.assertIn('machine learning', skills)
        self.assertIn('data structures', skills)
        self.assertIn('react', skills)

    def test_get_dynamic_skills_boundaries(self):
        """Test that short skills don't falsely trigger inside other words"""
        # 'c' is inside 'React' and 'clean', 'go' is inside 'Django'
        text = "I use React to write clean code. I also like Django."
        skills = get_dynamic_skills(text)
        
        self.assertNotIn('c', skills)
        self.assertNotIn('go', skills)
        self.assertIn('react', skills)
        self.assertIn('django', skills)

    def test_skill_match_scoring(self):
        """Test the final scoring math and difference logic"""
        resume = "I know Python, SQL, and AWS."
        jd = "Looking for a Python backend developer with SQL, AWS, and Docker experience."
        
        score, matched, missing = skill_match(resume, jd)
        
        self.assertEqual(len(matched), 3) # python, sql, aws
        self.assertIn('docker', missing)
        self.assertEqual(score, 75) # 3 out of 4 required skills matched