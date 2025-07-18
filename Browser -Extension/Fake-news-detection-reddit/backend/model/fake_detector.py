import numpy as np
import joblib
from tensorflow.keras.models import load_model
from sentence_transformers import SentenceTransformer

# Load models (only once)
minilm_model = SentenceTransformer('all-MiniLM-L6-v2')
scaler = joblib.load("model/scaler.pkl")
nn_model = load_model("model/fake_news_model.h5")

# Label mapping
label_map = {0: "REAL", 1: "FAKE"}

def predict_label(text: str, tabular: list):
    # Get MiniLM embedding
    embedding = minilm_model.encode([text])[0]  # shape = (384,)

    # Normalize tabular features
    tabular_scaled = scaler.transform([tabular])  # shape = (1, 5)

    # Concatenate features
    features = np.hstack([embedding, tabular_scaled[0]])  # shape = (389,)

    # Predict
    pred_prob = nn_model.predict(features.reshape(1, -1))[0][0]
    label = 1 if pred_prob >= 0.5 else 0

    return label_map[label], float(pred_prob)
