from django.utils.translation import ugettext_lazy as _


def phone_parser(phone: str, raise_exception=True):
    result = None
    phone = ''.join([letter for letter in phone if letter.isdigit()])
    if len(phone) < 11:
        if raise_exception:
            raise ValueError(_('Значение должно быть больше 9 символов'))
        return result
    result = f'+7{phone[-11:]}'

    return result
