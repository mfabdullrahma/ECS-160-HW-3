import os
os.environ.setdefault("GOOGLE_API_KEY", "test-key")

from unittest.mock import patch
import hashtagging_pb2
from hashtagging_service import HashtagServiceServicer, generate_hashtag


class FakeResponse:
    text = "#travel"

class FakeModels:
    def generate_content(self, model, contents):
        return FakeResponse()

class FakeClient:
    models = FakeModels()

class FakeModelsError:
    def generate_content(self, model, contents):
        raise RuntimeError("Gemini is in maintenance")

class FakeClientError:
    models = FakeModelsError()

class FakeResponseRefusal:
    text = "We cannot perform this request"

class FakeModelsActionRefusal:
    def generate_content(self, model, contents):
        return FakeResponseRefusal()

class FakeClientRefusal:
    models = FakeModelsActionRefusal()


@patch("hashtagging_service.client", FakeClient())
def test_1_generate_hashtag():
    assert generate_hashtag("I love traveling the world") == "#travel"


@patch("hashtagging_service.client", FakeClientError())
def test_2_model_error():
    assert generate_hashtag("I love trailmix") == "#bskypost"


@patch("hashtagging_service.client", FakeClientRefusal())
def test_3_model_refusal():
    assert generate_hashtag("scam") == "#bskypost"


@patch("hashtagging_service.generate_hashtag", return_value="#sad") 
def test_4_grpc_servicer(mock_gen):
    reply = HashtagServiceServicer().GetHashtag(
        hashtagging_pb2.HashtagRequest(post_content="boohoo"), context = None)
    assert reply.hashtag == "#sad"
    mock_gen.assert_called_once_with("boohoo")