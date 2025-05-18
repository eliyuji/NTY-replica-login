
import pytest
from app import app, db 
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv(dotenv_path=".env.test")

@pytest.fixture #https://docs.pytest.org/en/6.2.x/fixture.html to mock client
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_apicall(client):
    res = client.get("/api/articles?q=Sacramento")
    assert res.status_code == 200
    data = res.get_json()
    assert "response" in data
    assert "docs" in data["response"]
    assert isinstance(data["response"]["docs"], list) #https://www.w3schools.com/python/ref_func_isinstance.asp


def test_insertcomment():
    comment = {
        "article_url": "http://test.com/article",
        "user": {"id": "1", "username": "NYTtest"},
        "content": "this is a test",
        "timestamp": "2025-05-18T10:03:30Z",
        "edited": False,
        "replies": []
    }
    result = db.comments.insert_one(comment)
    inserted = db.comments.find_one({"_id": result.inserted_id})
    assert inserted["content"] == "Test comment"
    db.comments.delete_one({"_id": result.inserted_id})

def test_replyandcomment(client):
    with client.session_transaction() as sess:
        sess['user'] = {"email": "user@hw3.com", "sub": "1"}
    res = client.post("/api/comments", json={
        "article_url": "http://test.com/article",
        "content": "test comment"
    })
    assert res.status_code == 200
    comment = res.get_json()
    comment_id = comment["_id"]
    res = client.post(f"/api/comments/{comment_id}/reply", json={
        "content": "reply test"
    })
    assert res.status_code == 200
    assert res.get_json()["message"] == "reply test add"
    db.comments.delete_one({"_id": ObjectId(comment_id)})
