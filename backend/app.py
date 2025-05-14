from flask import Flask, jsonify, send_from_directory, request, redirect, session
import os
from flask_cors import CORS
from pymongo import MongoClient
import requests
import logging
import secrets

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

app = Flask(__name__, static_folder=static_path, template_folder=template_path)
app.secret_key = secrets.token_hex(16)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})

@app.route('/api/key')
def get_key():
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

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
    response = redirect("http://localhost:5173")
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

        return redirect("http://localhost:5173")

    except Exception as e:
        app.logger.exception("Error in /auth/callback")
        return f"Internal Server Error: {str(e)}", 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)),debug=debug_mode)