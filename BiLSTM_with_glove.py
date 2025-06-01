import pandas as pd
import numpy as np
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Bidirectional, LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# Step 1: Load Cleaned Data
df = pd.read_csv("cleaned_combined_dataset.csv")  # Make sure this path is correct

# === Choose the label column ===
label_column = '2_way_label'  # Change to '3_way_label' or '6_way_label' as needed

texts = df['cleaned_title'].astype(str).tolist()
labels = df[label_column].astype(int).tolist()

# Step 2: Tokenization
tokenizer = Tokenizer(num_words=50000, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
word_index = tokenizer.word_index
print(f"Found {len(word_index)} unique tokens.")

# Optional: Save tokenizer
with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

# Step 3: Padding
max_length = max(len(seq) for seq in sequences)
X = pad_sequences(sequences, maxlen=max_length, padding='post')

# Step 4: Prepare Labels and Class Info
num_classes = len(set(labels))

if num_classes == 2:
    y = np.array(labels)
    output_units = 1
    final_activation = 'sigmoid'
    loss_fn = 'binary_crossentropy'
else:
    y = to_categorical(labels, num_classes=num_classes)
    output_units = num_classes
    final_activation = 'softmax'
    loss_fn = 'categorical_crossentropy'

# Step 5: Load GloVe Embeddings (300d)
embedding_index = {}
glove_path = "glove.840B.300d.txt"  # Ensure this is the correct path

print("Loading GloVe embeddings...")
with open(glove_path, encoding='utf8') as f:
    for line in f:
        values = line.strip().split()
        word = values[0]
        coeffs = np.asarray(values[1:], dtype='float32')
        embedding_index[word] = coeffs

embedding_dim = 300
embedding_matrix = np.zeros((len(word_index) + 1, embedding_dim))

missing_count = 0
for word, i in word_index.items():
    embedding_vector = embedding_index.get(word)
    if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector
    else:
        missing_count += 1
print(f"{missing_count} words not found in GloVe.")

# Step 6: Build Bi-LSTM Model
model = Sequential([
    Embedding(len(word_index) + 1, embedding_dim, weights=[embedding_matrix], input_length=max_length, trainable=False),
    Bidirectional(LSTM(128, return_sequences=True)),
    Dropout(0.5),
    Bidirectional(LSTM(64)),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(output_units, activation=final_activation)
])

model.compile(loss=loss_fn, optimizer='adam', metrics=['accuracy'])
model.summary()

# Step 7: Train/Test Split and Training
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

history = model.fit(X_train, y_train, epochs=10, batch_size=64, validation_data=(X_test, y_test))

# Step 8: Save the model
model.save("bi_lstm_fake_news_model.h5")
print("Model saved successfully!")
