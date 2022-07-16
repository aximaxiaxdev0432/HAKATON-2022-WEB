from .parse_phone_util import phone_parser
from .send_sms_util import send_sms
from .passed_log_class import PassedLogClass


def render_inline_word(word):
    if word:
        return f'{word}, '
    else:
        return ''
