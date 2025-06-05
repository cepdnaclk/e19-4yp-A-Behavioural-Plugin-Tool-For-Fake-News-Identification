import praw

# Initialize Reddit client with your credentials
reddit = praw.Reddit(
    client_id='CLIENT_ID',
    client_secret='CLIENT_SECRET',
    user_agent='USER_AGENT'
)

post_id = "1l15b6s"
submission = reddit.submission(id=post_id)


# Fetch basic post data
print("Title          :", submission.title)
print("Upvote Ratio   :", submission.upvote_ratio)
print("Number of Comments :", submission.num_comments)

# Check for image URL
image_url = None
if hasattr(submission, 'preview') and 'images' in submission.preview:
    image_url = submission.preview['images'][0]['source']['url']
    print("Image URL      :", image_url)
else:
    print("Image URL      : No image found")

# Fetch all comments (flattened)
submission.comments.replace_more(limit=None)
all_comments = submission.comments.list()
print(f"Total Comments Fetched: {len(all_comments)}")

# Print first 10 comments as sample
for i, comment in enumerate(all_comments[:], start=1):
    print(f"Comment {i}: {comment.body[:150]}")