import csv
import requests
import sys

import pandas as pd
import requests

moderation_url = "http://localhost:8001/moderate"

class Post:
    cid: str
    author_handle: str
    created_at: str
    text: str
    reply_count: int
    like_count: int

    def __init__(self, cid, author_handle, created_at, text, reply_count, like_count):
        self.cid = cid
        self.author_handle = author_handle
        self.created_at = created_at
        self.text = text
        self.reply_count = reply_count
        self.like_count = like_count


def load_posts(input_path):
    df = pd.read_csv(input_path)
    return df


def get_top_posts(posts, limit=10):
    df_top10 = posts.nlargest(limit, "like_count")

    return [ Post(row.cid,
                  row.author_handle,
                  row.created_at,
                  row.text,
                  row.reply_count,
                  row.like_count) for row in df_top10.itertuples()]

def send_to_pipeline(post_content):
    """
    Send a post to the moderation service.
    Returns the hashtag string on success, or 'FAILED' if moderation fails.
    """
    payload = {"post_content" : post_content}
    r = requests.post(moderation_url, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["result"]


def process_post(post, index):
    result = send_to_pipeline(post.text)

    print(f"Post {index}: (@{post.author_handle}, {post.like_count} likes)")

    if (result == "FAILED"):
        print("[DELETED]")
    else:
        print(f"{post.text} {result}")
    
    


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "input.csv"

    posts = load_posts(input_path)
    top_posts = get_top_posts(posts, limit=10)

    print(f"Processing {len(top_posts)} most-liked posts...\n")

    for i, post in enumerate(top_posts, start=1):
       process_post(post, i)


if __name__ == "__main__":
    main()
