import spacy
import pandas as pd

nlp = spacy.load("en_core_web_sm")

df = pd.read_csv("demonyms.csv", header=None)
df.dropna(inplace=True)
demonym_to_country = {str(row[0]).strip(): str(row[1]).strip() for row in df.values}

text = "Serbians Told: Don't Throw Grenades in the Trash"

print("GPEs from spaCy:")
doc = nlp(text)
for ent in doc.ents:
    if ent.label_ == "GPE":
        print(ent.text)

print("\nDemonyms detected (using lemmatization):")
for token in doc:
    lemma = token.lemma_.lower()
    for demonym in demonym_to_country:
        if lemma == demonym.lower():
            print(f"{demonym_to_country[demonym]}")
