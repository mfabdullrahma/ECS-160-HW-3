import grpc
from concurrent import futures
import os

from google import genai

import hashtagging_pb2
import hashtagging_pb2_grpc

# Configure Gemini
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
MODEL = "gemini-3.5-flash-lite"
DEFAULT_TAG = "#bskypost"
PROMPT = ("Read this social media post and reply with exactly one hashtag that describes it."
          " For example, like #vacation or #travel. Reply with the hashtag only.\n\n Post: {post}")



def generate_hashtag(post_content):
    try:
        response = client.models.generate_content(model=MODEL, contents=PROMPT.format(post = post_content))
        text = response.text.strip()
        tokens = text.split()

        if tokens:
            tag = tokens[0]
            if tag.startswith("#"):
                return tag

        return DEFAULT_TAG
    except Exception as e:
        print(f"Gemini error: {e}", flush=True)
        return DEFAULT_TAG
    

class HashtagServiceServicer(hashtagging_pb2_grpc.HashtagServiceServicer):
    def GetHashtag(self, request, context):
        return hashtagging_pb2.HashtagResponse(hashtag=generate_hashtag(request.post_content))


def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    hashtagging_pb2_grpc.add_HashtagServiceServicer_to_server(HashtagServiceServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC server listening on port {port}")
    server.wait_for_termination()



if __name__ == "__main__":
    serve()



