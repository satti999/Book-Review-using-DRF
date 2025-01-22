import jwt
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

class JWTAuthentication(BaseAuthentication):
    """Custom authentication class for JWT"""

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None  # No authentication provided

        token = auth_header.split(" ")[1]  # Extract token from "Bearer <token>"

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        # Retrieve user from payload
        try:
            user = User.objects.get(email=payload["email"])
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, token)  # DRF expects (user, auth)
