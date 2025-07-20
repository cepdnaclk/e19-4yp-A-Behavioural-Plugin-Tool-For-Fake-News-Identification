import torch
from torch import nn
from transformers import BertModel

class DualBERTModel(nn.Module):
    def __init__(self, numeric_input_dim, num_regions, region_embed_dim=16):
        super().__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')  # shared BERT encoder
        self.region_embedding = nn.Embedding(num_regions, region_embed_dim)
        self.dropout = nn.Dropout(0.3)
        # Combine: title CLS vector + caption CLS vector + numeric features + region embedding
        self.fc1 = nn.Linear(768*2 + numeric_input_dim + region_embed_dim, 128)
        self.fc2 = nn.Linear(128, 1)
        self.relu = nn.ReLU()

    def forward(self, input_ids_title, attention_mask_title,
                input_ids_caption, attention_mask_caption,
                numerics, region_ids):
        # Get [CLS] embeddings from BERT for title and caption
        cls_title = self.bert(input_ids=input_ids_title, attention_mask=attention_mask_title).last_hidden_state[:, 0, :]
        cls_caption = self.bert(input_ids=input_ids_caption, attention_mask=attention_mask_caption).last_hidden_state[:, 0, :]
        region_embeds = self.region_embedding(region_ids)
        
        # Concatenate all features
        combined = torch.cat((cls_title, cls_caption, numerics, region_embeds), dim=1)
        x = self.relu(self.fc1(self.dropout(combined)))
        output = torch.sigmoid(self.fc2(x))  # output between 0 and 1
        
        return output
