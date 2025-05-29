from nrclex import NRCLex
import pandas as pd

# Load your cleaned comments
df = pd.read_csv("cleaned_comments.csv")

# Function to get dominant emotion(s) from a comment
def extract_emotions(text):
    if not isinstance(text, str) or not text.strip():
        return ""

    emotion = NRCLex(text)
    # Optional: Filter emotions with scores > 0
    return ', '.join(emotion.top_emotions) if emotion.top_emotions else ""

# Apply emotion extraction
df["emotions"] = df["clean_body"].apply(extract_emotions)

# Save the result
df.to_csv("emotion_annotated_comments.csv", index=False)

print("✅ Emotion analysis complete. File saved as emotion_annotated_comments.csv")
