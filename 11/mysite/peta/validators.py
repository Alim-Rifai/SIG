import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """
    Validates that a password meets strength requirements:
    - Minimum 8 characters
    - Maximum 128 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """

    def validate(self, password, user=None):
        errors = []

        if len(password) < 8:
            errors.append(
                _("Password must be at least 8 characters long.")
            )
        if len(password) > 128:
            errors.append(
                _("Password must be at most 128 characters long.")
            )
        if not re.search(r'[A-Z]', password):
            errors.append(
                _("Password must contain at least one uppercase letter.")
            )
        if not re.search(r'[a-z]', password):
            errors.append(
                _("Password must contain at least one lowercase letter.")
            )
        if not re.search(r'\d', password):
            errors.append(
                _("Password must contain at least one digit.")
            )
        if not re.search(r'[^A-Za-z0-9]', password):
            errors.append(
                _("Password must contain at least one special character.")
            )

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "Your password must be 8–128 characters and include at least "
            "one uppercase letter, one lowercase letter, one digit, and "
            "one special character."
        )


def validate_datprof_tahun(value):
    """Validate that tahun is an integer between 2000 and 2100 inclusive."""
    if not isinstance(value, int):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                _("Tahun must be a valid integer.")
            )

    if value < 2000 or value > 2100:
        raise ValidationError(
            _("Tahun must be between 2000 and 2100.")
        )


def validate_datprof_jumlah(value):
    """Validate that jumlah is greater than or equal to 0."""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(
            _("Jumlah must be a valid number.")
        )

    if numeric_value < 0:
        raise ValidationError(
            _("Jumlah must be greater than or equal to 0.")
        )


def validate_form_params(data_id, tahun):
    """
    Validate peta view query parameters.

    Args:
        data_id: Should be a positive integer referencing an existing NamaData record.
        tahun: Should be an integer between 2000 and 2100.

    Returns:
        A dict of errors if any validation fails, e.g. {"data_id": "message", "tahun": "message"}.
        None if all parameters are valid.
    """
    from peta.models import NamaData

    errors = {}

    # Validate data_id
    if data_id is not None:
        try:
            data_id_int = int(data_id)
            if data_id_int <= 0:
                errors["data_id"] = "data_id must be a positive integer."
            else:
                if not NamaData.objects.filter(pk=data_id_int).exists():
                    errors["data_id"] = (
                        "data_id does not reference an existing data record."
                    )
        except (TypeError, ValueError):
            errors["data_id"] = "data_id must be a valid integer."
    else:
        errors["data_id"] = "data_id is required."

    # Validate tahun
    if tahun is not None:
        try:
            tahun_int = int(tahun)
            if tahun_int < 2000 or tahun_int > 2100:
                errors["tahun"] = "Tahun must be between 2000 and 2100."
        except (TypeError, ValueError):
            errors["tahun"] = "Tahun must be a valid integer."
    else:
        errors["tahun"] = "Tahun is required."

    return errors if errors else None
