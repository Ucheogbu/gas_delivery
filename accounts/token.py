import datetime
from functools import wraps
from accounts.models import APIKey, User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.conf import settings as st
from jwt import encode, decode

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.verified)
        )


account_activation_token = TokenGenerator()

jwt_secret = st.JWT_SECRET


def get_jwt_token(user: User) -> str:
    return encode({'id': user.user_id, 'email': user.email, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, jwt_secret, algorithm="HS256")

def decode_jwt_token(token: str) -> User or None:
    return decode(token, jwt_secret)

