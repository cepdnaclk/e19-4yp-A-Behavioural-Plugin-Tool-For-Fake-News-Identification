from lime.lime_text import LimeTextExplainer
from transformers import BertTokenizer
import torch
import numpy as np

from model.model_loader import model, device, scaler, region2id  # Assuming model is loaded here

explainer = LimeTextExplainer(class_names=['Real', 'Fake'])
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
numeric_mean = scaler.mean_
region_mapping = {v: k for k, v in region2id.items()}  # id -> region

def lime_predict_proba(texts):
    # Dummy numeric + region info for now (will be overwritten in live case)
    batch_numeric = torch.tensor(np.tile(numeric_mean, (len(texts), 1)), dtype=torch.float32).to(device)
    batch_region_ids = torch.tensor([0] * len(texts), dtype=torch.long).to(device)

    tokens = tokenizer(
        texts,
        padding='max_length',
        truncation=True,
        max_length=32,
        return_tensors='pt'
    )

    input_ids = tokens['input_ids'].to(device)
    attention_mask = tokens['attention_mask'].to(device)

    with torch.no_grad():
        probs = model(input_ids, attention_mask, batch_numeric, batch_region_ids)
        probs = torch.cat([1 - probs, probs], dim=1)
    return probs.cpu().numpy()
