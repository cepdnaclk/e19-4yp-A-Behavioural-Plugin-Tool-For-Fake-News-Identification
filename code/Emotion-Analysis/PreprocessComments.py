# PreprocessComments.py
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
import warnings
import pandas as pd


warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
# Download NLTK stopwords if not already present
nltk.download('stopwords')

# Initialize resources
stop_words = set(stopwords.words('english'))
spell = SpellChecker()
correction_cache = {}

#Remove repeated characters (e.g., "soooo" → "soo")
def reduce_repeated_chars(text):
    return re.sub(r'(.)\1{2,}', r'\1\1', text)

#Expand contractions (e.g., "don't" → "do not")
def expand_contractions(text):
    return contractions.fix(text)


# Correct spelling with caching
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

#using the emoji representation dataset - https://www.kaggle.com/datasets/uom190346a/emoji-presentation-dataset
def load_emoji_dict_from_csv(csv_path):
    df = pd.read_csv(csv_path, encoding='utf-8')
    emoji_dict = dict(zip(df['Representation'], df['Name']))
    return emoji_dict

def replace_emojis_custom(text, emoji_dict):
    if not isinstance(text, str):
        return text
    for emoji_char, word in emoji_dict.items():
        text = text.replace(emoji_char, f" {word} ")
    return text

#load emojis dataset
emoji_dict = load_emoji_dict_from_csv("cleaned_emojis.csv")

# 5. Clean function applying all steps
def clean_text(text):
    if not isinstance(text, str):
        return text
    # 1. Replace emojis using your dataset
    text = replace_emojis_custom(text, emoji_dict)

    # 2. Remove new lines and tabs
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    # 3. Strip HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()

    # 4. Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # 5. Remove accented characters
    text = unidecode.unidecode(text)

    # 6. Expand contractions
    text = expand_contractions(text)

    # 7. Remove special characters except ! and ?
    text = re.sub(r"[^a-zA-Z0-9!? ]", " ", text)

    # 8. Reduce repeated characters
    text = reduce_repeated_chars(text)

    # 9. Correct misspelled words
    #text = correct_spelling(text)

    # 10. Remove stopwords
    words = [word for word in text.split() if word.lower() not in stop_words]
    text = ' '.join(words)

    # 11. Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

#Load and preprocess CSV file with comments
if __name__ == "__main__":
    input_path = 'cleaned_output.csv'
    output_path = 'cleaned_comments.csv'

    # Handle mixed data types warning
    df = pd.read_csv(input_path, low_memory=False)

    # Apply cleaning function
    df['clean_body'] = df['body'].apply(clean_text)

    # Save cleaned data
    df.to_csv(output_path, index=False)

    print(f"✅ Cleaned data saved to {output_path}")
