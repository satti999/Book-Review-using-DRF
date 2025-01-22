
from django.conf import settings
import jwt

def generate_jwt_token(useremail):
    payload = {
        'email': useremail
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token