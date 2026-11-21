from fastapi import FastAPI
from pydantic import BaseModel
import grpc
import os

import hashtagging_pb2
import hashtagging_pb2_grpc


app = FastAPI()

hashtag_addr = os.environ.get("HASHTAG_ADDR", "localhost:50051")

BANNED_WORDS = [
    "illegal",
    "fraud",
    "scam",
    "exploit",
    "dox",
    "swatting",
    "hack",
    "crypto",
    "bots"
]

class ModerateRequest(BaseModel):
    post_content: str


class ModerateResponse(BaseModel):
    result: str


def check_moderation(text):
    text_lower_case = text.lower()
    for ban_word in BANNED_WORDS:
        if ban_word in text_lower_case:
            return False
    return True


def get_hashtag_from_service(post_content):
    with grpc.insecure_channel(hashtag_addr) as channel:
        stub = hashtagging_pb2_grpc.HashtagServiceStub(channel) 
        reply = stub.GetHashtag(hashtagging_pb2.HashtagRequest(post_content=post_content), timeout = 30)
        return reply.hashtag


@app.post("/moderate")
def moderate(request: ModerateRequest):
    if not check_moderation(request.post_content):
        return ModerateResponse(result="FAILED")
    return ModerateResponse(result=get_hashtag_from_service(request.post_content))
