import pandas as pd

# Load the cleaned comments
df = pd.read_csv("cleaned_comments.csv")

# Sort the comments so that those with the same submission_id appear together
df_sorted = df.sort_values(by=["submission_id", "ups"], ascending=[True, False])

# Overwrite the original file
df_sorted.to_csv("cleaned_comments.csv", index=False)

print("✅ Grouped and sorted comments saved back to cleaned_comments.csv")
