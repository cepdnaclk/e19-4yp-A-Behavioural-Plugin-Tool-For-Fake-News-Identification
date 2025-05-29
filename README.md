___
# A Behavioural Plugin Tool for Fake News Identification 
___

## Abstract
The rapid spread of fake news on digital platforms poses significant risks, 
influencing public opinion and undermining trust in media. This proposal aims 
to enhance the accuracy of fake news detection by developing a multimodal 
system that integrates both text and image analysis. Recognizing that fake news 
often relies on misleading content in both formats, the project will explore 
various machine learning and deep learning models, incorporating advanced 
natural language processing (NLP) techniques for text analysis and emotional 
cues, as well as computer vision models for image classification. Additionally, 
user behaviour, such as likes, shares, and comments, will be analyzed to capture 
social network dynamics. The most effective model will be selected through 
performance evaluation and integrated into a browser plugin. This tool will 
provide users with a seamless, real-time interface for detecting fake news while 
browsing the web. The outcome will be an accurate, user-friendly, and efficient 
browser plugin that enhances content trustworthiness through advanced fake 
news detection. 

#### Fakeddit dataset

You can download the dataset [here](https://drive.google.com/drive/folders/1jU7qgDqU1je9Y0PMKJ_f31yXRo5uWGFm?usp=sharing).

#### Emojis dictionary
You can download emojis dictioary [here](https://www.kaggle.com/datasets/uom190346a/emoji-presentation-dataset).

#### 🔍😃Emotion Analysis
After cleaning and preprocessing, the final dataset is saved as cleaned_comments.csv inside the Emotion-Analysis directory. This file contains cleaned versions of the original comments with noise removed using a series of preprocessing steps.

🧹 Noise Removal Process
The following steps were performed to clean the raw comment text:
- Replace emojis with words – Convert emojis (e.g., 😳) into text labels (e.g., flushed face) using a custom emoji dictionary.
- Remove newlines and tabs – Flatten multi-line comments into single-line text.
- Strip HTML tags – Remove embedded HTML code from comments.
- Remove URLs – Eliminate links that do not contribute to emotion detection.
- Remove accented characters
- Expand contractions – Convert shortened words (e.g., “don’t”) to full form (“do not”).
- Remove special characters (except ! and ?) 
- Reduce repeated characters – Normalize exaggerated expressions (e.g., “soooo” → “soo”).
- Correct misspelled words 
- Remove stopwords
- Trim extra whitespaces


### ❕This installs all the required packages in one step.
pip install -r requirements.txt

