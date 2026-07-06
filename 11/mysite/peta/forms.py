from django import forms
from django.core.exceptions import ValidationError

from peta.models import Datprof

try:
    from peta.validators import validate_datprof_tahun, validate_datprof_jumlah
except ImportError:
    # Fallback validators if validators.py is not yet available (parallel task 2.2)
    def validate_datprof_tahun(value):
        if value is None:
            raise ValidationError('Tahun harus diisi.')
        if not isinstance(value, int):
            raise ValidationError('Tahun harus berupa bilangan bulat.')
        if value < 2000 or value > 2100:
            raise ValidationError(
                'Tahun harus antara 2000 dan 2100.',
                params={'value': value},
            )

    def validate_datprof_jumlah(value):
        if value is None:
            raise ValidationError('Jumlah harus diisi.')
        if value < 0:
            raise ValidationError(
                'Jumlah harus lebih besar atau sama dengan 0.',
                params={'value': value},
            )


class DatprofAdminForm(forms.ModelForm):
    """
    Admin form for the Datprof model with field-level validation.
    Validates tahun (2000–2100) and jumlah (>= 0) on submission,
    preserving form data on validation failure (default ModelForm behavior).
    """

    class Meta:
        model = Datprof
        fields = '__all__'

    def clean_tahun(self):
        tahun = self.cleaned_data.get('tahun')
        if tahun is None:
            raise ValidationError('Tahun harus diisi.')
        validate_datprof_tahun(tahun)
        return tahun

    def clean_jumlah(self):
        jumlah = self.cleaned_data.get('jumlah')
        if jumlah is None:
            raise ValidationError('Jumlah harus diisi.')
        validate_datprof_jumlah(jumlah)
        return jumlah
