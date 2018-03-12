import json
import jwt
import requests
import time


KEY_PATH = './my_key.json'

GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:jwt-bearer'


class Client(object):

    def __init__(self):
        self.session = requests.Session()

    def request(self, method, url, **kwargs):
        # First request will always need to obtain a token first
        if 'Authorization' not in self.session.headers:
            self.obtain_token()

        # Optimistically attempt to dispatch reqest
        response = self.session.request(method, url, **kwargs)
        if self.token_has_expired(response):
            # We got an 'Access token expired' response => refresh token
            self.obtain_token()
            # Re-dispatch the request that previously failed
            response = self.session.request(method, url, **kwargs)

        return response

    def token_has_expired(self, response):
        status = response.status_code
        content_type = response.headers['Content-Type']

        if status == 401 and content_type == 'application/json':
            body = response.json()
            if body.get('error_description') == 'Access token expired':
                return True

        return False

    def obtain_token(self):
        print "Obtaining token..."
        private_key, client_id, user_id, token_uri = self.load_private_key()

        iat = int(time.time())
        exp = iat + (60 * 60)
        claim_set = {
            "iss": client_id,
            "sub": user_id,
            "aud": token_uri,
            "exp": exp,
            "iat": iat,
        }
        grant_token = jwt.encode(claim_set, private_key, algorithm='RS256')
        payload = {'grant_type': GRANT_TYPE, 'assertion': grant_token}
        response = requests.post(token_uri, data=payload)
        token = response.json()['access_token']
        # Update session with fresh token
        self.session.headers.update({'Authorization': 'Bearer %s' % token})

    def load_private_key(self):
        keydata = json.load(open(KEY_PATH, "rb"))
        private_key = keydata['private_key'].encode('utf-8')
        client_id = keydata['client_id']
        user_id = keydata['user_id']
        token_uri = keydata['token_uri']
        return private_key, client_id, user_id, token_uri


def main():
    client = Client()
    # Issue a series of API requests an an example
    client.session.headers.update({'Accept': 'application/json'})

    for i in range(10):
        response = client.request('GET', 'http://localhost:8080/fd/')
        print response.status_code
        time.sleep(1)


if __name__ == '__main__':
    main()
