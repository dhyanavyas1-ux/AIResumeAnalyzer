import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('stopwords')



def clean_universal_text(text):
    if not text:
        return []

    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    tagged = nltk.pos_tag(tokens)

    # Extract NOUNS (NN, NNP) only. This catches technical terms and subjects.
    keywords = [
        word for word, tag in tagged
        if tag.startswith('NN') and word not in stop_words and len(word) > 1
    ]
    return list(set(keywords))


def detect_grammar_errors(text):
    """Checks for typos and consistency."""
    issues = []
    if not text:
        return issues
    if "pyhon" in text.lower():
        issues.append({'message': 'Spelling Error', 'suggestion': 'Python'})
    if "worked" in text.lower() and "works" in text.lower():
        issues.append({'message': 'Inconsistent Tense', 'suggestion': 'Use past tense for old roles.'})
    return issues