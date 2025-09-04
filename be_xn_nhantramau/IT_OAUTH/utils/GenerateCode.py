from django.utils.crypto import get_random_string
from hashlib import sha256
from datetime import datetime
from django.conf import settings


# Code for access_token
def GenerationCodeToken():
    # Generate a random string to use as the access token
    access_token = settings.CLIENT_ID + get_random_string(length=32) + settings.CLIENT_SECRET + datetime.now().strftime(
        '%Y%m%d')

    # Hash the access token using SHA-256
    hashed_access_token = sha256(access_token.encode()).hexdigest()

    return hashed_access_token
