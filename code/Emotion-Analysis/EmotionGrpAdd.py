import pandas as pd
from collections import defaultdict
import re
from nltk.stem import WordNetLemmatizer

# Load cleaned comments
df = pd.read_csv("cleaned_comments.csv")

# Load NRC lexicon
nrc_path = r"C:\Users\Student\Documents\FYP\code\NRC-Emotion-Lexicon\NRC-Emotion-Lexicon\NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"
nrc_lexicon = defaultdict(set)

with open(nrc_path, "r", encoding="utf-8") as file:
    for line in file:
        word, emotion, assoc = line.strip().split('\t')
        if int(assoc) == 1:
            nrc_lexicon[word].add(emotion)

# Define emotion groups
nrc_8_emotions = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}
novelty_emotions = {"fear", "disgust", "surprise"}
expectation_emotions = {"anticipation", "sadness", "joy", "trust"}

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Tokenizer with lemmatization
def tokenize(text):
    tokens = re.findall(r"\b\w+\b", str(text).lower())
    return [lemmatizer.lemmatize(token) for token in tokens]

# Emotion classification function
def classify_emotion_and_group(text):
    if not isinstance(text, str) or not text.strip():
        return pd.Series(["neutral", "none", "none"])

    tokens = tokenize(text)
    emotion_count = defaultdict(int)

    for token in tokens:
        for emotion in nrc_lexicon.get(token, []):
            if emotion in nrc_8_emotions:
                emotion_count[emotion] += 1

    # Filter non-zero emotions only
    non_zero_emotions = {e: c for e, c in emotion_count.items() if c > 0}

    # Grouping logic
    novelty_score = sum(emotion_count[e] for e in novelty_emotions)
    expectation_score = sum(emotion_count[e] for e in expectation_emotions)

    if novelty_score > expectation_score:
        group = "novelty"
    elif expectation_score > novelty_score:
        group = "expectation"
    else:
        group = "neutral"

    if non_zero_emotions:
        dominant_emotion = max(non_zero_emotions, key=non_zero_emotions.get)
        emotion_list = sorted(non_zero_emotions.keys())
        emotion_list_str = ", ".join(emotion_list)
    else:
        dominant_emotion = "none"
        emotion_list_str = "none"

    return pd.Series([group, dominant_emotion, emotion_list_str])

# Apply classification
df[["emotion_group", "dominant_emotion", "emotion_list"]] = df["clean_body"].apply(classify_emotion_and_group)

# Normalize emotion group
group_map = {"expectation": 0, "neutral": 0.5, "novelty": 1}
df["emotion_group_normalized"] = df["emotion_group"].map(group_map)

# Save results
df.to_csv("grouped_emotions_from_lexicon.csv", index=False)
print("Emotion classification with dominant + multiple emotions complete.")
