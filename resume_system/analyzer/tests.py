from django.test import TestCase

from analyzer.nlp_engine import ai_grammar_integrity_check, ai_tone_authenticity_check, detect_spelling_errors, detect_grammar_errors, ai_content_likelihood


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

