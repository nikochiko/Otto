from flask import Flask, request

from . import db
from . import spotify


app = Flask(__name__)


@app.route("/spotify/callback")
def spotify_save_token():
    user_id = request.args["state"]
    code = request.args.get["code"]

    token = spotify.get_access_token(code=code)

    db.set_value("spotify_token", user_id, token)

    return "Connected. You can close this page now"
