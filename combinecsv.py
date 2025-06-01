import pandas as pd

# Load cleaned files
train_df = pd.read_csv("cleaned_train_with_labels.csv")
valid_df = pd.read_csv("cleaned_validate_with_labels.csv")
test_df  = pd.read_csv("cleaned_test_with_labels.csv")

# Combine into one dataset (optional - only if needed for training/analysis)
combined_df = pd.concat([train_df, valid_df, test_df], ignore_index=True)

# Drop rows with any missing values
combined_df.dropna(inplace=True)

# Save to a new CSV
combined_df.to_csv("cleaned_combined_dataset.csv", index=False)

print("Combined dataset saved to 'cleaned_combined_dataset.csv")
