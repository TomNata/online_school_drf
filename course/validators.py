import re

from rest_framework.exceptions import ValidationError


class UrlValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        tmp_val = dict(value).get(self.field)
        if tmp_val:
            if not bool(re.findall('youtube.com', tmp_val)):
                raise ValidationError('URL should be youtube.com')



