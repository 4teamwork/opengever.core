import requests
import time

SERVICE_URL = 'https://apitest.onegovgever.ch/'
PORTAL_URL = 'https://apitest.onegovgever.ch/portal'
LOGIN_URL = PORTAL_URL + '/api/login'
TICKET_URL = PORTAL_URL + '/api/cas/tickets'

USERNAME = "john.doe"
PASSWORD = "secret"


class Client(object):

    def __init__(self):
        self.portal_session = requests.Session()
        self.service_session = requests.Session()
        self.portal_session.headers.update({'Accept': 'application/json'})
        self.service_session.headers.update({'Accept': 'application/json'})

    def request(self, method, url, **kwargs):
        # First request will always need to obtain a token first
        if 'Authorization' not in self.service_session.headers:
            self.obtain_token()

        # Optimistically attempt to dispatch reqest
        response = self.service_session.request(method, url, **kwargs)
        if self.token_has_expired(response):
            # We got an 'Access token expired' response => refresh token
            self.obtain_token()
            # Re-dispatch the request that previously failed
            response = self.service_session.request(method, url, **kwargs)

        return response

    def token_has_expired(self, response):
        status = response.status_code
        content_type = response.headers['Content-Type']

        if status == 401 and content_type == 'application/json':
            return True

        return False

    def obtain_token(self):
        print("Obtaining token...")

        # Login to portal using /api/login endpoint
        self.portal_session.post(
            LOGIN_URL,
            json={"username": USERNAME, "password": PASSWORD}
        )

        # Get CSRF token that was returned by server in a cookie
        csrf_token = self.portal_session.cookies['csrftoken']

        # Send the CSRF token as a request header in subsequent requests
        self.portal_session.headers.update({'X-CSRFToken': csrf_token})
        self.portal_session.headers.update({'Referer': PORTAL_URL})

        # Once logged in to the portal, get a CAS ticket
        ticket_response = self.portal_session.post(
            TICKET_URL,
            json={"service": SERVICE_URL}
        )
        ticket = ticket_response.json()['ticket']

        # Use ticket to authenticate to the @caslogin endpoint on the service
        login_response = self.portal_session.post(
            SERVICE_URL + "/@caslogin",
            json={'ticket': ticket, 'service': SERVICE_URL}
        )

        # Get the short lived JWT token from the @caslogin response, and send
        # it as a Bearer token in subsequent requests to the service
        token = login_response.json()['token']
        self.service_session.headers['Authorization'] = 'Bearer %s' % token


def main():
    client = Client()

    # Issue a series of API requests an an example
    for i in range(10):
        response = client.request('GET', SERVICE_URL)
        print(response.status_code)
        time.sleep(1)


if __name__ == '__main__':
    main()
