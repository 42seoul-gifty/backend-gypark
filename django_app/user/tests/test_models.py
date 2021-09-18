from django.test import Client

from allauth.socialaccount.models import SocialApp

from ..models import User


def get_dummy_user(email, password):
    user = User(email=email)
    user.set_password(password)
    user.save()
    return user


def get_jwt(email, password):
    get_dummy_user(email, password)
    client = Client()
    response = client.post('/login', {'email': email, 'password': password})
    return response.json()['data']


def jwt_to_headers(jwt):
    return {'HTTP_AUTHORIZATION': f'Bearer {jwt.get("access_token")}'}


def get_dummy_socialapp(**kwargs):
    socialapp = SocialApp.objects.create(**kwargs)
    socialapp.sites.add(1)
    return socialapp

