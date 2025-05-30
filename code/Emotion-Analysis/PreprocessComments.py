import re
import html
import unidecode
import contractions
import emoji
import nltk
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning
from spellchecker import SpellChecker
from nltk.corpus import stopwords
import pandas as pd
import swifter
import warnings

# Ignore certain BeautifulSoup warnings
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Download NLTK stopwords if not already present
nltk.download('stopwords')

# Initialize stopwords and spell checker
stop_words = set(stopwords.words('english'))
spell = SpellChecker()
correction_cache = {}

# Reduce repeated characters (e.g., "soooo" → "soo")
def reduce_repeated_chars(text):
    return re.sub(r'(.)\1{2,}', r'\1\1', text)

# Expand contractions (e.g., "don't" → "do not")
def expand_contractions(text):
    return contractions.fix(text)

# Correct spelling with caching (optional, currently disabled for performance)
def correct_spelling(text):
    corrected = []
    for word in text.split():
        if word.lower() in stop_words:
            corrected.append(word)
        else:
            if word in correction_cache:
                corrected_word = correction_cache[word]
            else:
                fixed = spell.correction(word)
                corrected_word = fixed if fixed is not None else word
                correction_cache[word] = corrected_word
            corrected.append(corrected_word)
    return ' '.join(corrected)

# Load emoji dictionary from CSV
def load_emoji_dict_from_csv(csv_path):
    df = pd.read_csv(csv_path, encoding='utf-8')
    emoji_dict = dict(zip(df['Representation'], df['Name']))
    return emoji_dict

# Replace emojis with words
def replace_emojis_custom(text, emoji_dict):
    if not isinstance(text, str):
        return text
    for emoji_char, word in emoji_dict.items():
        text = text.replace(emoji_char, f" {word} ")
    return text

# Load emoji mappings
emoji_dict = load_emoji_dict_from_csv("cleaned_emojis.csv")

# Full cleaning pipeline
def clean_text(text):
    if not isinstance(text, str):
        return text

    text = replace_emojis_custom(text, emoji_dict)
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = unidecode.unidecode(text)
    text = expand_contractions(text)
    text = re.sub(r"[^a-zA-Z0-9!? ]", " ", text)
    text = reduce_repeated_chars(text)
    # text = correct_spelling(text)  # Optional - slow
    words = [word for word in text.split() if word.lower() not in stop_words]
    text = ' '.join(words)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Main script to process in chunks with Swifter
if __name__ == "__main__":
    input_path = 'cleaned_comments.csv'
    output_path = 'preprocess_comments.csv'
    chunk_size = 100000

    reader = pd.read_csv(input_path, chunksize=chunk_size, low_memory=False)
    first = True

    for i, chunk in enumerate(reader):
        print(f"🔄 Processing chunk {i+1}...")
        chunk['clean_body'] = chunk['body'].swifter.apply(clean_text)
        chunk.to_csv(output_path, mode='w' if first else 'a', index=False, header=first)
        first = False
        print(f"Finished chunk {i+1}")

    print(f"All chunks processed and saved to {output_path}")
