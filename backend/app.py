from flask import Flask, jsonify, send_from_directory, request, redirect, session
import os
from flask_cors import CORS
from pymongo import MongoClient
import requests
import logging
import secrets
from datetime import datetime
from bson.objectid import ObjectId


static_path = os.getenv('STATIC_PATH','static')
template_path = os.getenv('TEMPLATE_PATH','templates')
# Mongo connection
mongo_uri = os.getenv("MONGO_URI")
mongo = MongoClient(mongo_uri)
db = mongo.get_default_database()

clientSecret = os.getenv("OIDC_CLIENT_SECRET")
clientID = os.getenv("OIDC_CLIENT_ID")
reDirect = 'http://localhost:8000/auth/callback'

DEX_TOKEN_URL = 'http://dex:5556/token'
DEX_USERINFO_URL = 'http://dex:5556/userinfo'

NYT_API_KEY = os.getenv("NYT_API_KEY")
frontend_url = os.getenv("FRONTEND_URL")

app = Flask(__name__, static_folder=static_path, template_folder=template_path)
app.secret_key = secrets.token_hex(16)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": frontend_url}})

@app.route('/api/key')
def get_key():
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

@app.route("/api/articles")
def get_articles():
    query = request.args.get("q", "Sacramento AND Davis")  
    url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json"
    params = {
        "q": query,
        "api-key": NYT_API_KEY
    }
    try:
        res = requests.get(url, params=params)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error in apikey "}), 500

@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    if path != '' and os.path.exists(os.path.join(static_path,path)):
        return send_from_directory(static_path, path)
    if path == 'login.html':
        return send_from_directory(static_path, 'login.html')
    return send_from_directory(template_path, 'index.html')

@app.route("/test-mongo")
def test_mongo():
    return jsonify({"collections": db.list_collection_names()})

@app.route("/auth/user")
def get_logged_in_user():
    user = session.get('user')
    app.logger.debug(f"Session user: {user}")  # Log the session state

    # Explicitly check if the session is empty and return 401 if no user is logged in
    if user is None:
        app.logger.debug("No user found in session.")
        return jsonify({"user": None}), 401
    return jsonify(user)
@app.route("/logout")
def logout():
    session.clear()
    response = redirect(frontend_url)
    response.set_cookie('session', '', expires=0)
    return response

@app.route("/auth/callback")
def auth_callback():
    try:
        code = request.args.get("code")
        if not code:
            return "Missing Code", 400

        token_resp = requests.post(DEX_TOKEN_URL, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': reDirect,
            'client_id': clientID,
            'client_secret': clientSecret
        }, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        if token_resp.status_code != 200:
            app.logger.error(f"Token response error: {token_resp.text}")
            return f"Failed to get token: {token_resp.text}", 500

        token_data = token_resp.json()
        access_token = token_data.get('access_token')

        if not access_token:
            return "No access token received", 500

        userinfo_resp = requests.get(DEX_USERINFO_URL, headers={
            'Authorization': f'Bearer {access_token}'
        })

        if userinfo_resp.status_code != 200:
            app.logger.error(f"Userinfo response error: {userinfo_resp.text}")
            return f"Failed to get user info: {userinfo_resp.text}", 500

        userinfo = userinfo_resp.json()
        session['user'] = userinfo

        return redirect(frontend_url)
    except Exception as e:
        app.logger.exception("Error in /auth/callback")
        return f"error in callback", 500

@app.route("/api/comments", methods=["GET"])
def get_comments():
    article_url = request.args.get("url")
    comments = list(db.comments.find({"article_url": article_url}))
    for c in comments:
        c["_id"] = str(c["_id"])
    return jsonify(comments)


@app.route("/api/comments", methods=["POST"])
def post_comment():
    user = session.get("user")
    data = request.json
    email = user.get("email", "")
    username = email.split("@")[0]

    comment = {
        "article_url": data["article_url"],
        "user": {
            "id": user.get("sub"),
            "username": username
        },
        "content": data["content"],
        "timestamp": datetime.now(),
        "edited": False,
        "replies": []
    }

    result = db.comments.insert_one(comment) # https://www.mongodb.com/docs/manual/reference/method/db.collection.insertOne/
    comment["_id"] = str(result.inserted_id) # 

    return jsonify(comment)



@app.route("/api/comments/<comment_id>/reply", methods=["POST"])
def reply_comment(comment_id):
    user = session.get("user")
    data = request.json
    email = user.get("email", "")
    username = email.split("@")[0]
    reply = {
        "user": {
            "id": user.get("sub"),
            "username": username
        },
        "content": data.get("content", ""),
        "timestamp": datetime.now()
    }
    db.comments.update_one({"_id": ObjectId(comment_id)}, {"$push": {"replies": reply}}) #https://www.mongodb.com/docs/manual/reference/method/db.collection.updateOne/
    return jsonify({"message": "Reply added"})


@app.route("/api/comments/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    user = session.get("user")
    email = user.get("email", "")
    username = email.split("@")[0]
    role = username.upper()
    try:
        db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": {
                "content": f"COMMENT REMOVED BY {role}!",
                "edited": True
            }}
        )
        return jsonify({"message": "Comment redacted"})
    except Exception as e:
        return jsonify({"error in Delete commment"}), 500


@app.route("/api/comments/<comment_id>/reply/<int:reply_index>", methods=["DELETE"])
def delete_reply(comment_id, reply_index):
    user = session.get("user")
    email = user.get("email", "")
    username = email.split("@")[0]
    try:
        obj_id = ObjectId(comment_id)
        comment = db.comments.find_one({"_id": obj_id})
        replies = comment.get("replies", [])
        replies[reply_index]["content"] = f"REPLY REMOVED BY {username.upper()}!"
        replies[reply_index]["edited"] = True
        replies[reply_index]["timestamp"] = datetime.now()

        db.comments.update_one(
            {"_id": obj_id},
            {"$set": {"replies": replies}}
        )
        return jsonify({"message": "Reply edited"})

    except Exception as e:
        return jsonify({"error in Delete reply"}), 500
    


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)),debug=debug_mode)
