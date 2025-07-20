import os
import requests
import torch
import joblib
from transformers import BertTokenizer
import numpy as np
from model.dual_bert_model import DualBERTModel
import gdown


# Extracted Google Drive file ID
MODEL_PATH = "model/model_drive.pth"
FILE_ID = "1lrqPNL5fqkmC5cR4YjVRwVELQhAYYbkW"
MODEL_URL = f"https://drive.google.com/uc?id={FILE_ID}"

def download_model_if_needed():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model using gdown...")
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        gdown.download(MODEL_URL, MODEL_PATH, quiet=False)
        print("Download complete.")
    else:
        print("Model already exists locally.")

download_model_if_needed()

scaler = joblib.load("model/scaler.pkl")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
label_map = {0: "FAKE", 1: "REAL"}
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
num_regions = 19
numeric_input_dim = 6
model = DualBERTModel(numeric_input_dim=numeric_input_dim, num_regions=num_regions)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=False))
model.to(device)
model.eval()

def predict_label(title: str, tabular: list, caption: str = "", region_id: int = 0):
    """
    Predict fake/real label and confidence for a post
    :param title: Post title string
    :param tabular: List of numeric features (e.g. [num_comments, score, ...])
    :param caption: Image caption string (optional)
    :param region_id: Numeric region id (default 0)
    :return: label string, confidence float (0 to 1)
    """

    # Preprocess numeric features (scale)
    tabular_scaled = scaler.transform([tabular])  # shape (1, numeric_input_dim)

    # Tokenize title and caption
    title_tokens = tokenizer(title, padding='max_length', truncation=True, max_length=32, return_tensors='pt')
    caption_tokens = tokenizer(caption, padding='max_length', truncation=True, max_length=32, return_tensors='pt')

    # Move inputs to device
    input_ids_title = title_tokens['input_ids'].to(device)
    attention_mask_title = title_tokens['attention_mask'].to(device)
    input_ids_caption = caption_tokens['input_ids'].to(device)
    attention_mask_caption = caption_tokens['attention_mask'].to(device)
    numerics_tensor = torch.tensor(tabular_scaled, dtype=torch.float32).to(device)
    region_tensor = torch.tensor([region_id], dtype=torch.long).to(device)

    with torch.no_grad():
        prob = model(
            input_ids_title,
            attention_mask_title,
            input_ids_caption,
            attention_mask_caption,
            numerics_tensor,
            region_tensor
        )

    prob_value = prob.item()  # sigmoid output between 0 and 1
    pred_label = 1 if prob_value >= 0.5 else 0
    confidence = prob_value if pred_label == 1 else 1 - prob_value
    return label_map[pred_label], confidence
