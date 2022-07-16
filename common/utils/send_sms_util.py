from typing import Dict, Union

from django.contrib.auth import get_user_model

User = get_user_model()


def send_sms(phone_or_user: Union[User, str], text: str) -> None:
    pass
