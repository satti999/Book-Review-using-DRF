import jwt
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework import  exceptions, authentication


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # token = request.headers.get("token")
        auth_data = authentication.get_authorization_header(request).decode('utf-8')

        if not auth_data or not auth_data.startswith('Bearer '):
            return None

        token = auth_data.split(' ')[1]

        
        if not token:
            return Response({"error": "Token not provided"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            print("Token",token)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        # Retrieve user from payload
        try:
            email = payload.get("email") 
            if not email:
                raise ValueError("Email is missing from the token payload")

            print("Email:", email)

            user= User.objects.filter(email=email).first()
            if user is None:
                raise exceptions.AuthenticationFailed('User not found')
            return (user, None)
        
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')

        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
           

      

def auth_by_token(request):
    try:
        jwt_auth= JWTAuthentication()
        auth= jwt_auth.authenticate(request)
        if auth:
            return auth[0]
        else:
            return None
    except exceptions.AuthenticationFailed:
        return exceptions.AuthenticationFailed