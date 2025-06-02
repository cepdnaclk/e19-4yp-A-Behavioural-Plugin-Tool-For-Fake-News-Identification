import pandas as pd
import ftfy
import re
import html
import unidecode
import contractions
import emoji
import nltk
import warnings
import swifter
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from spellchecker import SpellChecker

# Setup
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Optional: spell checker
spell = SpellChecker()
correction_cache = {}

# Load emoji dictionary
def load_emoji_dict_from_csv(csv_path):
    df = pd.read_csv(csv_path, encoding='utf-8')
    return dict(zip(df['Representation'], df['Name']))

emoji_dict = load_emoji_dict_from_csv("cleaned_emojis.csv")

# Load NRC Lexicon
nrc_path = r"C:\Users\Student\Documents\FYP\code\NRC-Emotion-Lexicon\NRC-Emotion-Lexicon\NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"
nrc_lexicon = defaultdict(set)

with open(nrc_path, "r", encoding="utf-8") as file:
    for line in file:
        word, emotion, assoc = line.strip().split('\t')
        if int(assoc) == 1:
            nrc_lexicon[word].add(emotion)

# Emotion categories
nrc_8_emotions = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}
novelty_emotions = {"fear", "disgust", "surprise"}
expectation_emotions = {"anticipation", "sadness", "joy", "trust"}
group_map = {"expectation": 0, "neutral": 0.5, "novelty": 1}

# Cleaning & Preprocessing Functions
def fix_mojibake(text):
    return ftfy.fix_text(text) if pd.notnull(text) else text

def reduce_repeated_chars(text):
    return re.sub(r'(.)\1{2,}', r'\1\1', text)

def expand_contractions(text):
    return contractions.fix(text)

def correct_spelling(text):  # Optional: very slow
    corrected = []
    for word in text.split():
        if word.lower() in stop_words:
            corrected.append(word)
        else:
            if word in correction_cache:
                corrected_word = correction_cache[word]
            else:
                fixed = spell.correction(word)
                corrected_word = fixed if fixed else word
                correction_cache[word] = corrected_word
            corrected.append(corrected_word)
    return ' '.join(corrected)

def replace_emojis_custom(text, emoji_dict):
    for emoji_char, word in emoji_dict.items():
        text = text.replace(emoji_char, f" {word} ")
    return text

def clean_text_pipeline(text):
    if not isinstance(text, str): return text
    text = replace_emojis_custom(text, emoji_dict)
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = unidecode.unidecode(text)
    text = expand_contractions(text)
    text = re.sub(r"[^a-zA-Z0-9!? ]", " ", text)
    text = reduce_repeated_chars(text)
    words = [word for word in text.split() if word.lower() not in stop_words]
    text = ' '.join(words)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    tokens = re.findall(r"\b\w+\b", str(text).lower())
    return [lemmatizer.lemmatize(token) for token in tokens]

def classify_emotion_and_group(text):
    if not isinstance(text, str) or not text.strip():
        return pd.Series(["neutral", "none", "none", 0.5])
    tokens = tokenize(text)
    emotion_count = defaultdict(int)
    for token in tokens:
        for emotion in nrc_lexicon.get(token, []):
            if emotion in nrc_8_emotions:
                emotion_count[emotion] += 1
    non_zero_emotions = {e: c for e, c in emotion_count.items() if c > 0}
    novelty_score = sum(emotion_count[e] for e in novelty_emotions)
    expectation_score = sum(emotion_count[e] for e in expectation_emotions)
    group = "neutral"
    if novelty_score > expectation_score:
        group = "novelty"
    elif expectation_score > novelty_score:
        group = "expectation"
    dominant_emotion = max(non_zero_emotions, key=non_zero_emotions.get) if non_zero_emotions else "none"
    emotion_list_str = ", ".join(sorted(non_zero_emotions.keys())) if non_zero_emotions else "none"
    return pd.Series([group, dominant_emotion, emotion_list_str, group_map[group]])

# Master Pipeline Function
def process_all_in_one(input_path, output_path, chunk_size=100000):
    first = True
    for i, chunk in enumerate(pd.read_csv(input_path, chunksize=chunk_size, encoding='latin1', low_memory=False)):
        print(f"🔄 Processing chunk {i+1}...")
        chunk['body'] = chunk['body'].swifter.apply(fix_mojibake)
        chunk['clean_body'] = chunk['body'].swifter.apply(clean_text_pipeline)
        emotion_data = chunk['clean_body'].swifter.apply(classify_emotion_and_group)
        emotion_data.columns = ['emotion_group', 'dominant_emotion', 'emotion_list', 'emotion_group_normalized']
        processed_chunk = pd.concat([chunk, emotion_data], axis=1)
        processed_chunk.to_csv(output_path, mode='w' if first else 'a', index=False, header=first, encoding='utf-8-sig')
        first = False
        print(f"✅ Finished chunk {i+1}")
    print(f"🎉 All chunks processed and saved to {output_path}")

# Run the pipeline
if __name__ == "__main__":
    input_path = "all_commentsCSV.csv"
    output_path = "final_emotion_processed_comments.csv"
    process_all_in_one(input_path, output_path)
