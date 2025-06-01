import pandas as pd
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK resources (run only once)
nltk.download('stopwords')
nltk.download('wordnet')

# Text cleaning function
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)              # Remove URLs
    text = re.sub(r'@\w+|#\w+|r/\w+|u/\w+', '', text)                # Remove mentions, hashtags, subreddit/user
    text = text.translate(str.maketrans('', '', string.punctuation)) # Remove punctuation
    text = re.sub(r'\d+', '', text)                                  # Remove digits
    text = re.sub(r'\s+', ' ', text).strip()                         # Normalize spaces

    stop_words = set(stopwords.words('english'))
    words = text.split()
    words = [w for w in words if w not in stop_words]

    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(w) for w in words]

    return ' '.join(words)

# === Step 1: Load your dataset ===
# 🔁 Replace this with your actual CSV file path
file_path = r"C:\Users\ADMIN\Desktop\Semester 08\CO425 FYP II\reddit\Fakeddit\all_samples (also includes non multimodal)\all_train.csv"
df = pd.read_csv(file_path)

# === Step 2: Clean the title column ===
df['cleaned_title'] = df['title'].apply(clean_text)

# === Step 3: Keep only cleaned titles + labels ===
# 🔁 Change '2_way_label' if you're using a different label column like '3_way_label'
df_cleaned = df[['cleaned_title', '2_way_label','3_way_label','6_way_label']]

# === Step 4: Save the cleaned data ===
output_path = "cleaned_train_with_labels.csv"  # Change filename for valid/test
df_cleaned.to_csv(output_path, index=False)

print(f"Cleaned file saved to: {output_path}")
