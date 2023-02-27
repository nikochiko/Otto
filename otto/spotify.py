import base64
import requests

from . import config


client_id = config.spotify_client_id
client_secret = config.spotify_client_secret
redirect_uri = config.spotify_redirect_uri
auth_base_url = config.spotify_auth_base_url
api_base_url = config.spotify_api_base_url


def get_authorize_url(*, state=None, scope=None):
    query_params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
    }
    if state:
        query_params.update({"state": state})
    if scope:
        query_params.update({"scope": scope})

    query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
    url = f"{auth_base_url}/authorize?{query_string}"

    return url


def get_access_token(*, code):
    url = auth_base_url + "/api/token"

    basic_auth_value = get_basic_auth_value(client_id, client_secret)
    r = requests.post(
        url,
        headers={"Authorization": f"Basic {basic_auth_value}"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        })
    r.raise_for_status()
    return r.json()["access_token"]


def get_headers(*, token, **extras):
    return {
        "Accept": "application/json", "Authorization": f"Bearer {token}",
        **extras
    }


def get_play_state(token):
    endpoint = "/v1/me/player"
    url = api_base_url + endpoint

    r = requests.get(url, headers=get_headers(token=token))
    r.raise_for_status()
    return r.content and r.json() or ""


def get_basic_auth_value(username, password):
    return base64.b64encode(f"{username}:{password}".encode()).decode(encoding="utf-8")
