import pandas as pd

# Load the cleaned comments
df = pd.read_csv("cleaned_comments.csv")

# Sort the comments so that those with the same submission_id appear together
df_sorted = df.sort_values(by=["submission_id", "ups"], ascending=[True, False])

# Save the grouped result to a new file
df_sorted.to_csv("grouped_sorted_comments.csv", index=False)

print("✅ Grouped comments saved to grouped_sorted_comments.csv")
