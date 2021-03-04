import requests


def get_ris_token():
    return "exGH5kE7CF7gz3smhF7v4dhs"


def make_ris_url(path):
    return "http://localhost:8000/api/{}".format(path)


def make_ris_session():
    session = requests.Session()
    session.headers = {"Authorization": "Token {}".format(get_ris_token())}
    return session
