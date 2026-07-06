from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from peta.models import Datprof, Provinsi, NamaData


class DatprofResource(resources.ModelResource):
    """
    Import/Export resource for the Datprof model.

    Export: resolves foreign keys to human-readable names (province name, namadata nama).
    Import: validates FK existence and field ranges per row, reporting errors with row numbers.
    """

    # For export: show province name instead of raw ID
    provinsi = fields.Field(
        column_name='provinsi',
        attribute='provinsi',
        widget=ForeignKeyWidget(Provinsi, 'name')
    )
    # For export: show namadata nama instead of raw ID
    namadata = fields.Field(
        column_name='namadata',
        attribute='namadata',
        widget=ForeignKeyWidget(NamaData, 'nama')
    )

    class Meta:
        model = Datprof
        fields = ('id', 'provinsi', 'namadata', 'tahun', 'jumlah')
        import_id_fields = ['id']
        export_order = ('id', 'provinsi', 'namadata', 'tahun', 'jumlah')

    def before_import_row(self, row, row_number=None, **kwargs):
        """
        Row-level validation during import.
        Checks FK existence and field value ranges before the row is saved.
        Raises Exception with combined error messages for all invalid fields.
        """
        errors = []

        # Validate provinsi FK existence
        provinsi_val = row.get('provinsi') or row.get('provinsi_id')
        if provinsi_val:
            # Try lookup by name first (ForeignKeyWidget uses 'name' field)
            if not Provinsi.objects.filter(name=provinsi_val).exists():
                # Fallback: try as numeric ID
                try:
                    provinsi_id = int(provinsi_val)
                    if not Provinsi.objects.filter(pk=provinsi_id).exists():
                        errors.append(
                            f"provinsi '{provinsi_val}' does not exist"
                        )
                except (TypeError, ValueError):
                    errors.append(
                        f"provinsi '{provinsi_val}' does not exist"
                    )
        else:
            errors.append("provinsi is required")

        # Validate namadata FK existence
        namadata_val = row.get('namadata') or row.get('namadata_id')
        if namadata_val:
            # Try lookup by nama first (ForeignKeyWidget uses 'nama' field)
            if not NamaData.objects.filter(nama=namadata_val).exists():
                # Fallback: try as numeric ID
                try:
                    namadata_id = int(namadata_val)
                    if not NamaData.objects.filter(pk=namadata_id).exists():
                        errors.append(
                            f"namadata '{namadata_val}' does not exist"
                        )
                except (TypeError, ValueError):
                    errors.append(
                        f"namadata '{namadata_val}' does not exist"
                    )
        else:
            errors.append("namadata is required")

        # Validate tahun field range (must be integer between 2000 and 2100)
        tahun = row.get('tahun')
        if tahun is not None and str(tahun).strip() != '':
            try:
                tahun_int = int(tahun)
                if tahun_int < 2000 or tahun_int > 2100:
                    errors.append(
                        f"tahun '{tahun}' must be between 2000 and 2100"
                    )
            except (TypeError, ValueError):
                errors.append(f"tahun '{tahun}' must be a valid integer")
        else:
            errors.append("tahun is required")

        # Validate jumlah field range (must be numeric >= 0)
        jumlah = row.get('jumlah')
        if jumlah is not None and str(jumlah).strip() != '':
            try:
                jumlah_float = float(jumlah)
                if jumlah_float < 0:
                    errors.append(f"jumlah '{jumlah}' must be >= 0")
            except (TypeError, ValueError):
                errors.append(f"jumlah '{jumlah}' must be a valid number")
        else:
            errors.append("jumlah is required")

        if errors:
            row_info = f" (row {row_number})" if row_number else ""
            raise Exception(f"Validation failed{row_info}: " + '; '.join(errors))
