from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import praw
import joblib
from textblob import TextBlob
from collections import Counter

from model.fake_detector import predict_label
from model.emotion_pipeline import classify_emotion_group  # Real NRC-based function
from model.regional_pipeline import classify_region
from model.image_caption_pipeline import caption_image_url
from model.duplication_counter import DuplicationCounter

# Load .env
load_dotenv()

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace "*" with specific origin or extension ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
dup_counter = DuplicationCounter("C:/Users/user/Downloads/Fake-news-detection-reddit/backend/data/Fakeddit-dataset-final.csv")
region2id = joblib.load("model/region2id.pkl")
# Setup Reddit API
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Request model
class PostRequest(BaseModel):
    post_id: str

# Compute polarity using TextBlob
def get_polarity(text: str) -> float:
    return TextBlob(text).sentiment.polarity

# Compute emotion score from top 100 comments
def get_emotion_score_from_comments(submission) -> float:
    try:
        submission.comments.replace_more(limit=0)
        comments = submission.comments.list()
        if not comments:
            return -1.0

        scores = [classify_emotion_group(c.body) for c in comments[:100]]
        count = Counter(scores)
        count_0 = count.get(0.0, 0)
        count_1 = count.get(1.0, 0)

        if count_0 > count_1:
            return 0.0
        elif count_1 > count_0:
            return 1.0
        else:
            return 0.5
    except Exception as e:
        print(f"⚠️ Error getting emotion score: {e}")
        return -1.0
# Get region ID from name
def get_region_id(region_name: str) -> int:
    return region2id.get(region_name.lower(), 0)  # 0 = unknown or default region

# Analyze API
@app.post("/analyze")
def analyze_post(data: PostRequest):
    print(f"📥 Received post ID: {data.post_id}")
    try:
        submission = reddit.submission(id=data.post_id)
        title = submission.title or ""
        selftext = submission.selftext or ""
        content = f"{title}\n{selftext}".strip()
        duplication_count = dup_counter.count_duplicates(content) # Count duplication from dataset
        # Tabular features
        num_comments = submission.num_comments or 0
        score = submission.score or 0
        upvote_ratio = submission.upvote_ratio or 1.0
        polarity = get_polarity(content)
        emotion_score = get_emotion_score_from_comments(submission)
        sub_region = classify_region(content)
        image_url = None
        if hasattr(submission, 'preview') and 'images' in submission.preview:
            image_url = submission.preview['images'][0]['source']['url']

        # Generate caption
        caption = caption_image_url(image_url) if image_url else "Image does not exist"
        tabular = tabular = [num_comments, score, upvote_ratio, polarity, emotion_score, duplication_count]

        region_id = get_region_id(sub_region)
        if region_id == -1:
            raise ValueError("Invalid region")

        # Predict
        label, confidence = predict_label(title, tabular, caption, region_id)
        print("🔎 Title:", title)
        print("📝 Selftext:", selftext)
        print("🖼️ Caption:", caption)
        print("📊 Tabular Features:")
        print("   - num_comments:", num_comments)
        print("   - score:", score)
        print("   - upvote_ratio:", upvote_ratio)
        print("   - polarity:", polarity)
        print("   - emotion_score:", emotion_score)
        print("📈 Duplication Count:", duplication_count)
        print("🧠 Prediction:")
        print("🌍 Region:", sub_region)
        print("   - Label:", label)
        print("   - Confidence:", round(confidence, 4))

        return {
            "label": label,
            "confidence": round(confidence, 4),
            "polarity": polarity,
            "emotion_score": emotion_score,
            "sub_region": sub_region
        }

    except Exception as e:
        import traceback
        print("🚨 Exception during analysis:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
