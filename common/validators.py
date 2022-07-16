import regex

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def validate_contact_phone(value):
    if value is None:
        pass
    else:
        if not regex.fullmatch(r'\380[\d]{9}', value):
            raise ValidationError(
                message=_("Номер телефон должен соответствовать 380XXXXXXXXX"))