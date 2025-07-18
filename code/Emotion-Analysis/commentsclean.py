import pandas as pd
import ftfy

# Clean function
def clean_text(text):
    if pd.isnull(text):
        return text
    return ftfy.fix_text(text)

input_file = 'FILE_PATH'
output_file = 'cleaned_output.csv'

chunk_size = 100000
first_chunk = True

# 👇 Use encoding='latin1' to preserve emoji corruption that ftfy can fix
for chunk in pd.read_csv(input_file, chunksize=chunk_size, encoding='latin1'):
    chunk['body'] = chunk['body'].apply(clean_text)
    chunk.to_csv(output_file, encoding= 'utf-8-sig', mode='w' if first_chunk else 'a', index=False, header=first_chunk)
    first_chunk = False
    break

print("All chunks processed and saved to 'cleaned_output.csv'")
