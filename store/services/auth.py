import time

import jwt
from google.auth.transport import requests
from rest_framework import status

from shop import settings
from store.serializers import *
from store.models import *
from rest_framework.response import Response


class LoginTokens:
    def __init__(self, payload_access, payload_refresh, token):
        self.access = jwt.encode(payload_access,
                                 settings.ACCESS_SECRET_KEY, algorithm='HS256')
        self.refresh = jwt.encode(payload_refresh,
                                  settings.REFRESH_SECRET_KEY, algorithm='HS256')
        self.refresh = str(self.refresh)[2:-1]
        self.response = Response()
        self.response.set_cookie(key='refresh', value=self.refresh, httponly=True)
        self.response.data = {
            'access': self.access,
            'email': parse_id_token(token['id_token'])['email'],
            'name': parse_id_token(token['id_token'])['name'],
            'picture': parse_id_token(token['id_token'])['picture'],
        }


def login(request, id_token):
    token = {'id_token': request.data.get('id_token')}

    try:
        idinfo = id_token.verify_oauth2_token(
            token['id_token'], requests.Request(),
            '29897898232-727dsvebqsfa7kqrddl0hhbbfalg0vjp.apps.googleusercontent.com'
        )
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        payloadAccess = {
            'email': parse_id_token(token['id_token'])['email'],
            'exp': time.time() + 15000
        }
        payloadRefresh = {
            'email': parse_id_token(token['id_token'])['email'],
            'exp': time.time() + 40000
        }
        try:
            User.objects.get(email=parse_id_token(token['id_token'])['email'])
            tokens = LoginTokens(payloadAccess, payloadRefresh, token)
            try:
                UserRefreshToken.objects.get(
                    user=User.objects.get(
                        email=parse_id_token(token['id_token'])['email'])
                )
                UserRefreshToken.objects.filter(
                    user=User.objects.get(
                        email=parse_id_token(
                            token['id_token'])['email'])).update(
                    refresh=tokens.refresh
                )
            except UserRefreshToken.DoesNotExist:
                UserRefreshToken.objects.create(
                    user=User.objects.get(
                        email=parse_id_token(
                            token['id_token'])['email']),
                    refresh=tokens.refresh
                )
            return tokens.response
        except User.DoesNotExist:
            User.objects.create_user(parse_id_token(token['id_token'])['name'],
                                     parse_id_token(token['id_token'])['email'])
            tokens = LoginTokens(payloadAccess, payloadRefresh, token)

            UserRefreshToken.objects.create(
                user=User.objects.get(
                    username=parse_id_token(token['id_token'])['name']),
                refresh=tokens.refresh
            )
            UserPhotoProfile.objects.create(
                user=User.objects.get(
                    username=parse_id_token(token['id_token'])['name']),
                picture=parse_id_token(token['id_token'])['picture']
            )
            return tokens.response
    except ValueError as err:
        print(err)
        content = {'message': 'Invalid token'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


def refresh_token(request):
    refreshEmail = parse_id_token(request.COOKIES['refresh'])['email']
    try:
        data = {'token': request.COOKIES['refresh']}
    except:
        return Response({'message': 'Auth failed1'},
                        status=status.HTTP_401_UNAUTHORIZED)
    payloadAccess = {
        'email': parse_id_token(data['token'])['email'],
        'exp': time.time() + 15000
    }
    payloadRefresh = {
        'email': parse_id_token(data['token'])['email'],
        'exp': time.time() + 40000
    }
    try:
        jwt.decode(data['token'], settings.REFRESH_SECRET_KEY,
                   algorithms='HS256')
    except jwt.ExpiredSignatureError:
        return Response({'message': 'Auth failed2'},
                        status=status.HTTP_401_UNAUTHORIZED)
    try:
        UserRefreshToken.objects.get(
            user=User.objects.get(
                email=refreshEmail)
        )
        if UserRefreshToken.objects.get(
                user=User.objects.get(
                    email=refreshEmail)).refresh == \
                request.COOKIES['refresh']:

            access = jwt.encode(payloadAccess, settings.ACCESS_SECRET_KEY)
            refresh = jwt.encode(payloadRefresh, settings.REFRESH_SECRET_KEY)
            refresh = str(refresh)[2:-1]

            UserRefreshToken.objects.filter(
                user=User.objects.get(
                    email=refreshEmail)).update(
                refresh=refresh
            )
            response = Response()
            response.set_cookie(key='refresh', value=refresh, httponly=True)
            response.data = {
                'access': access,
                'email': User.objects.get(email=refreshEmail).email,
                'name': User.objects.get(email=refreshEmail).username,
                'picture': UserPhotoProfile.objects.get(
                    user=User.objects.get(email=refreshEmail)).picture,
            }
            return response
        else:
            return Response({'message': 'Auth failed3'},
                            status=status.HTTP_401_UNAUTHORIZED)
    except UserRefreshToken.DoesNotExist:
        return Response({'message': 'Auth failed4'},
                        status=status.HTTP_401_UNAUTHORIZED)


def logout(request):
    try:
        data = parse_id_token(request.COOKIES['refresh'])['email']
        UserRefreshToken.objects.get(
            user=User.objects.get(
                email=data)).delete()
    except:
        return Response({'message': 'Auth failed'},
                        status=status.HTTP_401_UNAUTHORIZED)
    return Response({'message': 'Logout success'})