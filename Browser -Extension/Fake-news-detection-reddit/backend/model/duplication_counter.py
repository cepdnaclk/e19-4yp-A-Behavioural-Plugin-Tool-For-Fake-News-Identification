import pandas as pd

def normalize_title(text: str) -> str:
    if not isinstance(text, str):
        return ''
    text = text.strip()
    # Remove leading/trailing single or double quotes
    if text.startswith(("'", '"')) and text.endswith(("'", '"')):
        text = text[1:-1]
    return text.strip()

class DuplicationCounter:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        if 'title' not in self.df.columns:
            raise ValueError("Missing 'title' column in dataset")

        # Normalize titles here to remove quotes & extra spaces
        self.df['content'] = self.df['title'].fillna('').apply(normalize_title)
        self.content_counts = self.df['content'].value_counts()

    def count_duplicates(self, new_content: str) -> int:
        normalized_content = normalize_title(new_content)
        count = self.content_counts.get(normalized_content, 0)
        # If no match, count should be 1 (for this new unseen item)
        if count == 0:
            return 1
        else:
            return count
