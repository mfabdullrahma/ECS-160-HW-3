from unittest.mock import patch
from fastapi.testclient import TestClient
from moderation_service import app, check_moderation


client = TestClient(app)

def test_1_banned_word():
    assert not check_moderation("I hate getting crypto scams in my email.")

def test_2_safe_post():
    assert check_moderation("I went for a walk at the park.")

@patch("moderation_service.get_hashtag_from_service", return_value="#PokemonZA")
def test_3_return_hashtag(mock_grpc):
    r = client.post("/moderate", json ={"post_content": "I love playing Pokemon ZA."})
    assert r.json() == {"result": "#PokemonZA"}
    mock_grpc.assert_called_once_with("I love playing Pokemon ZA.")

@patch("moderation_service.get_hashtag_from_service")
def test_banned_post_no_hashtag(mock_grpc):
    r = client.post("/moderate", json ={"post_content": "I enjoy swatting streamers"})
    assert r.json() == {"result": "FAILED"}
    mock_grpc.assert_not_called()