import requests
import requests.auth
import validators
import logging

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
        self._client = client or WebApplicationClient(client_id, token=token)
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

    # def __init__(self, token):
    #     self.token = token
    # self.scope = scope

    # def post(self, token, ):

    def get_token(self, token_url, secret, secret_id, authorization_response, redirect_uri, scope, code,**kwargs):
        """method for fetch an access token from the token endpoint
        :param token_url: Token endpoint URL, must use HTTPS
        :param kwargs: Extra parameters for token request
        :return: tokens dictionary
        """
        print(secret, authorization_response)
        if not validators.url(token_url) or not token_url.lower().startswith('https://'):
            logger.warning('')
            raise Exception
        # body = (code=secret, body='', redirect_uri=redirect_uri, **kwargs)

        auth = requests.auth.HTTPBasicAuth(kwargs.get('client_id'), kwargs.get('secret'))
        headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded;charser=UTF-8'}
        # body = self._client.prepare_request_body(code=secret,
        #                                          redirect_uri=self.redirect_uri, **kwargs)
        # r = self.post(token_url, headers=headers, auth=auth)
        print(token_url)
        params = {
            'grant_type': 'client_credentials',
            'client_id': secret_id,
            'client_secret': secret,
            'code': code
        }

        print('---->requests get')
        # r = requests.get(token_url, params=params)
        r = requests.post(token_url, params=params)
        print('Rrrrr')
        print(r.json())
        print(r.json()['access_token'])
        # if r.json().get('access_token'):
        #     self.check_user_token(r.json()['access_token'])
        n = requests.get(
            # f'https://graph.facebook.com/me?fields={# scope}')
            f'https://graph.facebook.com/me/accounts')

        info = n.json()
        print(info)
        # r = requests.get(token_url, client_id=secret_id, redirect_uri=redirect_uri, client_secret=secret, scope=scope)

        # self.token = r.text, scope = self.scope
        token = {}
        return token

    # def check_user_token(self, access_token):
    #     # access_token = self.token_access()
    #     if access_token:
    #         params = {
    #             # 'input_token': token,
    #             'access_token': access_token
    #         }
    #         try:
    #             r = requests.get('https://graph.facebook.com/v3.3/debug_token',
    #                              params=params)
    #         except Exception as e:
    #             logger.warning(f"\n check token --> {e} \n")
    #         else:
    #             if r.json().get('data', 'error') != 'error':
    #                 expires_token = datetime.fromtimestamp(r.json().get('data')
    #                                                        [
    #                                                            'data_access_expires_at']).strftime(
    #                     "%Y-%m-%d")
    #                 return {'expire_token': expires_token,
    #                         'network_user_id': r.json().get('data')['user_id']}

