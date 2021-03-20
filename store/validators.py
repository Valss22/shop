from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_percent_field(value):
    if value > 100:
        raise ValidationError(
            _('%(value)s is not an percent'),
            params={'value': value},
        )


