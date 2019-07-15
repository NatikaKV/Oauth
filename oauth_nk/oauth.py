import re
import urllib
from urllib.parse import parse_qs
import requests
import requests.auth
import validators
import logging
import sys

logger = logging.getLogger(__name__)


class Oauth(requests.Session):
    def __init__(self, client_id=None, client=None, auto_refresh_url=None,
                 auto_refresh_kwargs=None, scope=None, redirect_uri=None, token=None,
                 state=None, token_updater=None, **kwargs):
        """Construct a new OAuth 2 client session.

        :param client_id: Client id obtained during registration
        :param client: :class:`oauthlib.oauth2.Client` to be used. Default is
                       WebApplicationClient which is useful for any
                       hosted application but not mobile or desktop.
        :param scope: List of scopes you wish to request access to
        :param redirect_uri: Redirect URI you registered as callback
        :param token: Token dictionary, must include access_token
                      and token_type.
        :param state: State string used to prevent CSRF. This will be given
                      when creating the authorization url and must be supplied
                      when parsing the authorization response.
                      Can be either a string or a no argument callable.
        :auto_refresh_url: Refresh token endpoint URL, must be HTTPS. Supply
                           this if you wish the client to automatically refresh
                           your access tokens.
        :auto_refresh_kwargs: Extra arguments to pass to the refresh token
                              endpoint.
        :token_updater: Method with one argument, token, to be used to update
                        your token database on automatic token refresh. If not
                        set a TokenUpdated warning will be raised when a token
                        has been refreshed. This warning will carry the token
                        in its token argument.
        :param kwargs: Arguments to pass to the Session constructor.
        """
        super(Oauth, self).__init__(**kwargs)
        # self._client = client or WebApplicationClient(client_id, token=token)
        self._client = client
        self.token = token or {}
        self.scope = scope
        self.redirect_uri = redirect_uri
        # self.state = state or generate_token
        # self._state = state
        self.auto_refresh_url = auto_refresh_url
        self.auto_refresh_kwargs = auto_refresh_kwargs or {}
        self.token_updater = token_updater

        # Allow customizations for non compliant providers through various
        # hooks to adjust requests and responses.
        self.compliance_hook = {
            'access_token_response': set(),
            'refresh_token_response': set(),
            'protected_request': set(),
        }

    def fetch_token_(self, token_url, code=None, authorization_response=None,
                     body='', auth=None, username=None, password=None, method='POST',
                     timeout=None, headers=None, verify=False, proxies=None, **kwargs):
        """Generic method for fetching an access token from the token endpoint.

        If you are using the MobileApplicationClient you will want to use
        token_from_fragment instead of fetch_token.

        :param token_url: Token endpoint URL, must use HTTPS.
        :param code: Authorization code (used by WebApplicationClients).
        :param authorization_response: Authorization response URL, the callback
                                       URL of the request back to you. Used by
                                       WebApplicationClients instead of code.
        :param body: Optional application/x-www-form-urlencoded body to add the
                     include in the token request. Prefer kwargs over body.
        :param auth: An auth tuple or method as accepted by requests.
        :param username: Username used by LegacyApplicationClients.
        :param password: Password used by LegacyApplicationClients.
        :param method: The HTTP method used to make the request. Defaults
                       to POST, but may also be GET. Other methods should
                       be added as needed.
        :param headers: Dict to default request headers with.
        :param timeout: Timeout of the request in seconds.
        :param verify: Verify SSL certificate.
        :param kwargs: Extra parameters to include in the token request.
        :return: A token dict
        """
        if not validators.url(token_url) or not token_url.lower().startswith('https://'):
            logger.warning('Not secure token_url')
            raise Exception

        body = dict(code=code, body=body, username=username, password=password, **kwargs)

        client_id = kwargs.get('client_id', '')
        if auth is None:
            if client_id:
                logger.debug('Encoding client_id "%s" with client_secret as Basic auth credentials.', client_id)
                client_secret = kwargs.get('client_secret', '')
                client_secret = client_secret if client_secret is not None else ''
                auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
            elif username:
                if password is None:
                    raise ValueError('Username was supplied, but not password.')
                logger.debug('Encoding username, password as Basic auth credentials.')
                auth = requests.auth.HTTPBasicAuth(username, password)

        headers = headers or {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        self.token = {}
        if method.upper() == 'POST':

            r = self.post(token_url, data=dict(body),
                          timeout=timeout, headers=headers, auth=auth,
                          verify=verify)
            logger.debug('Prepared fetch token request body %s', body)
        elif method.upper() == 'GET':
            # if method is not 'POST', switch body to querystring and GET
            r = self.get(token_url, params=dict(body), timeout=timeout, headers=headers, auth=auth)
            logger.debug('Prepared fetch token request querystring %s', body)
        else:
            raise ValueError('The method kwarg must be POST or GET.')

        logger.debug('Request to fetch token completed with status %s.',
                     r.status_code)
        logger.debug('Request headers were %s', r.request.headers)
        logger.debug('Request body was %s', r.request.body)
        logger.debug('Response headers were %s and content %s.',
                     r.headers, r.text)
        logger.debug('Invoking %d token response hooks.',
                     len(self.compliance_hook['access_token_response']))
        for hook in self.compliance_hook['access_token_response']:
            logger.debug('Invoking hook %s.', hook)
            r = hook(r)
        self.token = r.json().get('access_token')
        logger.debug('Obtained token %s.', self.token)
        return self.token

