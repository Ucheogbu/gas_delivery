from django.contrib.auth import get_user_model
import uuid
from accounts.util import get_api_key
from django.conf import settings as st
from accounts.token import get_jwt_token, decode_jwt_token


User = get_user_model()
tz = st.TZN
authprotocol = "jwt" if st.AUTH_PROTOCOL == "jwt" else "custom"


def get_current_date():
    africa = timezone(tz)
    return datetime.datetime.now(africa)


def generate_uuid(user_id):
    user_id = user_id
    us1 = user_id[:8]
    us2 = user_id[8:]
    rand = "".join(
        [random.choice(string.ascii_letters + string.digits) for n in range(16)]
    )
    return f"{us1}{rand}{us2}"


def create_or_update_user(
    email: str,
    phone_number: str,
    address: str,
    state: str,
    country: str,
    password: str,
    user_id: str = None,
    is_admin: bool = False,
    is_vendor: bool = False,
    is_customer: bool = True,
    is_active: bool = True,
):
    if not user_id:
        user_id = str(uuid.uuid4())
        try:
            user = UserData.objects.create(
                user_id=user_id,
                email=email,
                phone_number=phone_number,
                address=address,
                state=state,
                country=country,
                is_active=is_active,
                is_admin=is_admin,
                is_vendor=is_vendor,
                is_customer=is_customer,
            )
            user.set_password(password)
            user.save()
            key = get_api_key()
            APIKey.objects.create(user=user, api_key=key)
        except Exception as err:
            print(err)
            return None
        else:
            return {"user": user, "key": key}
    else:
        try:
            User.objects.filter(user_id=user_id).update(
                email=email,
                phone_number=phone_number,
                address=address,
                state=state,
                country=country,
                is_active=is_active,
                is_admin=is_admin,
                is_vendor=is_vendor,
                is_customer=is_customer,
            )
            user = User.objects.get(user_id=user_id)
            key = user.user_data.api_key

        except Exception as err:
            print(err)
            return None
        else:
            return {"user": user, "key": key}


def get_user_api_key(email: str, password: str):
    user = UserData.objects.get(email=email)
    if authprotocol != "jwt":
        if user.check_password(password):
            return user.user_data.api_key
        else:
            return None
    else:
        return get_jwt_token(user) if user else None


def change_api_key(email: str):
    if UserData.objects.filter(email=email):
        user = UserData.objects.get(email=email)
        key = get_api_key()
        APIKey.objects.filter(user=user).update(api_key=key)
        return key
    else:
        return None


def change_password(email: str, old_password, new_password):
    user = User.objects.get(email=email)
    if user:
        if not (old_password and new_password):
            return None
        key = user.api_key
        if user.check_password(old_password):
            user.set_password(new_password)
            return key
        else:
            return None
    else:
        return None


def delete_user(user_id: str):
    User.objects.filter(user_id=user_id).delete()
