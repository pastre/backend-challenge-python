import jwt
import requests
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from .models import TwoFAUser


class AppleOAuth2():
    """apple authentication backend"""

    name = 'apple'
    ACCESS_TOKEN_URL = 'https://appleid.apple.com/auth/token'
    SCOPE_SEPARATOR = ','
    ID_KEY = 'uid'

    def do_auth(self, access_token, username):
        print("AE CUSAO", access_token)
        """
        Finish the auth process once the access_token was retrieved
        Get the email from ID token received from apple
        """
        response_data = {}
        client_id, client_secret = self.get_key_and_secret()

        headers = {'content-type': "application/x-www-form-urlencoded"}
        data = {
            'client_id': 'pastre.github.io.ReflectionsApp',
            'client_secret': client_secret,
            'code': access_token,
            'grant_type': 'authorization_code',
        }

        res = requests.post(AppleOAuth2.ACCESS_TOKEN_URL, data=data, headers=headers)
        response_dict = res.json()
        id_token = response_dict.get('id_token', None)
        print(res.status_code, res.text)
        print("AE CUSAO",  response_dict)
        if id_token:
            decoded = jwt.decode(id_token, '', verify=False)
            response_data.update({'email': decoded['email']}) if 'email' in decoded else None
            response_data.update({'uid': decoded['sub']}) if 'sub' in decoded else None
            print("AE CUSAO", decoded, decoded['email'],  decoded['sub'], response_dict)

        response = {}
        response.update(response_data)
        response.update({'access_token': access_token}) if 'access_token' not in response else None

        user = TwoFAUser.objects.get(uid = response_data['uid'])

        if not user:
        		newUser = TwoFAUser(
        			email = response_data['email']
					uid = response_data['uid']
					username = username
					)
        		newUser.save()
        		user = newUser
        return user

        print("falow", response)

    def get_key_and_secret(self):
        headers = {
       		"alg": "ES256",
            'kid': settings.SOCIAL_AUTH_APPLE_KEY_ID
        }

        payload = {
            'iss': settings.SOCIAL_AUTH_APPLE_TEAM_ID,
            'iat': timezone.now(),
            'exp': timezone.now() + timedelta(days=180),
            'aud': 'https://appleid.apple.com',
            'sub': settings.CLIENT_ID,
        }

        client_secret = jwt.encode(
            payload, 
            settings.SOCIAL_AUTH_APPLE_PRIVATE_KEY, 
            algorithm='ES256', 
            headers=headers
        ).decode("utf-8")
        
        return settings.CLIENT_ID, client_secret