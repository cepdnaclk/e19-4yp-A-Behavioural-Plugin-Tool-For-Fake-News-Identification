import re, unidecode
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import defaultdict
import nltk

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Load NRC Lexicon
nrc_lexicon = defaultdict(set)
nrc_path = "model/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"

with open(nrc_path, "r", encoding="utf-8") as file:
    for line in file:
        word, emotion, assoc = line.strip().split('\t')
        if int(assoc) == 1:
            nrc_lexicon[word].add(emotion)

# Emotion groups
nrc_8_emotions = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}
novelty_emotions = {"fear", "disgust", "surprise"}
expectation_emotions = {"anticipation", "sadness", "joy", "trust"}
group_map = {"expectation": 0.0, "neutral": 0.5, "novelty": 1.0}

def clean_text(text: str) -> str:
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"http\S+|www\.\S+", '', text)
    text = unidecode.unidecode(text)
    text = re.sub(r"[^a-zA-Z0-9!? ]", " ", text)
    words = [w for w in text.split() if w.lower() not in stop_words]
    return ' '.join(words)

def tokenize(text: str):
    return [lemmatizer.lemmatize(w.lower()) for w in re.findall(r"\b\w+\b", text)]

def classify_emotion_group(text: str) -> float:
    if not isinstance(text, str) or not text.strip():
        return 0.5
    tokens = tokenize(clean_text(text))
    emotion_count = defaultdict(int)
    for token in tokens:
        for emotion in nrc_lexicon.get(token, []):
            if emotion in nrc_8_emotions:
                emotion_count[emotion] += 1

    novelty_score = sum(emotion_count[e] for e in novelty_emotions)
    expectation_score = sum(emotion_count[e] for e in expectation_emotions)

    if novelty_score > expectation_score:
        return 1.0
    elif expectation_score > novelty_score:
        return 0.0
    else:
        return 0.5
