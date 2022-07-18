from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from common.utils import phone_parser
from common.validators import validate_contact_phone
from common.widgets import PhoneWidget

User = get_user_model()


class BasePhoneForm(forms.Form):

    def clean_phone(self):
        try:
            phone = phone_parser(self.data['phone'])
        except ValueError:
            raise forms.ValidationError(_('Значение должно быть больше 9 символов, пример: 380XXXXXXXXX'), code='invalid')
        return phone


class RegistrationForm(BasePhoneForm):
    phone = forms.CharField(label='', max_length=16, widget=PhoneWidget(attrs={'placeholder': '+380ХХХХХХХХХХ'}))
    email = forms.CharField(label='', max_length=60)

    def clean_phone(self):
        """
        Validate that the username (phone number) exists
        """
        phone = super().clean_phone()
        if User.objects.filter(username__iexact=phone):
            return False
        return phone

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
