import requests
from django.conf import settings

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import YleTunnusProvider


class YleTunnusOAuth2Adapter(OAuth2Adapter):
    provider_id = YleTunnusProvider.id
    access_token_url = 'https://auth.api-test.yle.fi/v1/token'
    authorize_url = 'https://auth.api-test.yle.fi/v1/authorize'
    profile_url = 'https://auth.api-test.yle.fi/v1/userinfo'

    def __init__(self, *args, **kwargs):
        self.auth_conf = settings.SOCIALACCOUNT_PROVIDERS['yletunnus']['AUTH_PARAMS']
        app_params = '?app_id={}&app_key={}'.format(self.auth_conf['app_id'],
                                                    self.auth_conf['app_key'])
        self.access_token_url += app_params
        return super(YleTunnusOAuth2Adapter, self).__init__(*args, **kwargs)

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers, params=self.auth_conf)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(YleTunnusOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(YleTunnusOAuth2Adapter)
