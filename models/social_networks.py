import logging
import os
from flask import request
# from oauth_nk.oauth_nk import Oauth
import requests

from oauth_nk.oauth import Oauth

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

logger = logging.getLogger(__name__)


# class SocialAuth(Base):
# __tablename__ = 'social_networks'
# __table_args__ = {'mysql_charset': 'utf8',
#                   'mysql_collate': 'utf8_general_ci'}
# id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
# # user_id = Column(Integer, ForeignKey(f'{user_connections}'))
# email = Column(String(191))
# account = Column(String(91))
# account_id = Column(String(91))
# rank = Column(Integer)
# first_name = Column(String(100))
# last_name = Column(String(100))
# account_link = Column(String(255))
# image_url = Column(String(255))
# access_token = Column(String(255))
# secret = Column(String(255), nullable=True)
# refresh_token = Column(String(255))
# expires_time = Column(String(91))
class SocialAuth(object):
    def __init__(self, email=None, account=None, account_id=None, account_link=None, first_name=None, last_name=None,
                 image_url=None, access_token=None, secret=None, refresh_token=None,
                 expires_time=None):
        self.email = email
        self.account = account
        self.account_id = account_id
        self.account_link = account_link,
        self.first_name = first_name,
        self.last_name = last_name,
        self.image_url = image_url,
        self.access_token = access_token,
        self.secret = secret,
        self.refresh_token = refresh_token,
        self.expires_time = expires_time


class FBAuth(object):
    # authorization_base_url = 'https://www.facebook.com/v3.2/dialog/oauth?'
    authorization_base_url = 'https://www.facebook.com/dialog/oauth?'
    token_url = 'https://graph.facebook.com/oauth/access_token'

    # credentials from your app
    fb_client_id = '1000237797032...'
    fb_secret = '1607b1aebd91779669a6791c5270f...'
    # scope = 'email,  first_name, last_name, ink, birthday, picture'
    scope = 'email, name, link, picture'

    def get_facebook(self, root_uri=None):
        if root_uri:
            redirect_uri = root_uri + 'social/'
            facebook = requests.get(self.authorization_base_url,
                                    params={'client_id': self.fb_client_id, 'redirect_uri': redirect_uri + 'fb',
                                            'client_secret': self.fb_secret, 'code': self.scope, 'state': '123456'})
            return facebook

    def check_user_token(self, access_token):
        # access_token = self.token_access()
        if access_token:
            params = {
                'input_token': access_token,
                'access_token': access_token
            }
            try:
                r = requests.get('https://graph.facebook.com/v3.3/debug_token',
                                 params=params)
            except Exception as e:
                logger.warning(f"\n check token --> {e} \n")
                return False
            else:
                if r.json().get('data', 'error') != 'error':
                    expires_token = r.json().get('data')['data_access_expires_at']
                    return {'expire_token': expires_token,
                            'network_user_id': r.json().get('data')['user_id']}

    def get_user_info(self, user_id, token):
        try:
            params = {
                'fields': self.scope,
                'access_token': token,
            }
            r = requests.get(f'https://graph.facebook.com/{user_id}',
                             params=params)
        except Exception as e:
            logger.warning(f"\n get_user_info --> {e} \n")
        else:
            if r.json().get('email', 'error') != 'error':
                return r.json()

    def fetch_info(self, code):
        redirect_uri = request.url_root + 'social/fb'
        scope = 'email'
        token = Oauth().fetch_token_(self.token_url, client_secret=self.fb_secret, client_id=self.fb_client_id,
                                     authorization_response=request.url, redirect_uri=redirect_uri, scope=scope,
                                     code=code)
        expires_token = self.check_user_token(token)
        if expires_token:
            user_info = self.get_user_info(expires_token.get('network_user_id'), token)
            if user_info:
                return user_info
        else:
            logger.warning('')
            return False


class GoogleAuth(object):
    # OAuth endpoints (client_secret, client_id) given in the Google API doc.
    def __init__(self):
        self.authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://accounts.google.com/o/oauth2/token"
        self.scope = ["https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"]

        # credentials from your app
        self.go_client_id = '...77693294-adm133ie6enqs7hm5b1naloar94thefp.apps.googleusercontent.com'
        self.go_secret = '..sgZgBmh6BJW_8FIKuC...'

    def get_goo(self, root_url=None):
        redirect_url = root_url + 'social/goo'
        google = requests.get(self.authorization_base_url,
                              params={'client_id': self.go_client_id, 'scope': self.scope,
                                      'redirect_uri': redirect_url, 'include_granted_scopes': 'true',
                                      'access_type': 'offline', 'response_type': 'code', 'prompt': "select_account"})
        return google

    def fetch_info(self, code=None, state=None, root_url=None, user_id=None):
        redirect_url = root_url + 'social/goo'
        token = Oauth().fetch_token_(self.token_url, client_secret=self.go_secret, client_id=self.go_client_id,
                                     redirect_uri=redirect_url, scope=self.scope,
                                     code=code, grant_type='authorization_code')
        url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {token}'}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.json()
        else:
            logger.warning('some problem with getting data with google')
            return False


class LnAuth(object):
    def __init__(self):
        self.authorizations_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'

        # credentials from your app
        self.ln_client_id = '..2bp5dw3hu8..'
        self.ln_secret = 't..EAQi2Loz..'

    def get_ln(self, root_url=None):
        redirect_uri = root_url + 'social/ln'
        linkedln = requests.get(self.authorizations_base_url,
                                params={'response_type': 'code', 'client_id': self.ln_client_id,
                                        'redirect_uri': redirect_uri,
                                        'state': '123456',
                                        'scope': 'r_liteprofile r_emailaddress w_member_social'})
        return linkedln

    def fetch_info(self, code=None, root_url=None):
        redirect_url = root_url + 'social/ln'
        token = Oauth().fetch_token_(self.token_url, grant_type='authorization_code', code=code,
                                     redirect_uri=redirect_url,
                                     client_id=self.ln_client_id, client_secret=self.ln_secret)
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'x-li-format': 'json'}
        r = requests.get(
            'https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,profilePicture(displayImage~:playableStreams))',
            headers=headers)
        r_email = requests.get('https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
                               headers=headers)
        if r.status_code == 200:
            user = self.parse_data(r.json())
            user['email'] = r_email.json()['elements'][0]['handle~']['emailAddress']
            logger.info('successfully get user  info')
            return user
        else:
            logger.warning('some problem with getting data from linkedlin')
            return False

    def parse_data(self, data):
        user = {
            'first_name': data['firstName']['localized']['ru_RU'],
            'last_name': data['lastName']['localized']['ru_RU']
        }
        return user
#
#
# def upload_profile_image(self, img, name):
#     r = requests.get(img, allow_redirects=True)
#     if r.status_code == 200:
#         result = img.rstrip('.')
#
#         list = img.split(".")
#         res = list.pop()
#         path = f'{root_dir}/static/images/user_images/{name}.{res}'
#         with open(path, 'wb') as f:
#             for chunk in r:
#                 f.write(chunk)
#
#         return res
#
#
#
