from django.db import models

# Create your models here.
class Provinsi(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, default='')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    class Meta:
        db_table = 'provinces'
        verbose_name = 'Provinsi'
        verbose_name_plural = 'Provinsi'

    def __str__(self):
        return self.name
    
class Kabkota(models.Model):
    id = models.BigIntegerField(primary_key=True)
    province = models.ForeignKey(
        Provinsi, 
        on_delete=models.CASCADE, 
        db_column='province_id',  # Memastikan nama kolom di DB tetap 'province_id'
        related_name='kabkota_set'
    )
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, default='')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    class Meta:
        db_table = 'regencies'
        verbose_name = 'Kabupaten/Kota'
        verbose_name_plural = 'Kabupaten/Kota'

    def __str__(self):
        return self.name
    
class Kecamatan(models.Model):
    id = models.BigIntegerField(primary_key=True)
    regency = models.ForeignKey(
        Kabkota, 
        on_delete=models.CASCADE, 
        db_column='regency_id',  # Memastikan nama kolom di DB tetap 'regency_id'
        related_name='kecamatan_set'
    )
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, default='')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    class Meta:
        db_table = 'districts'
        verbose_name = 'Kecamatan'
        verbose_name_plural = 'Kecamatan'

    def __str__(self):
        return self.name
    
    # wilayah/models.py

class NamaData(models.Model):
    nama = models.CharField(max_length=255)

    class Meta:
        db_table = 'namadata'
        verbose_name = 'Nama Data'
        verbose_name_plural = 'Nama Data'

    def __str__(self):
        return self.nama

class Datprof(models.Model):
    provinsi = models.ForeignKey(Provinsi, on_delete=models.CASCADE, db_column='provinsi_id', related_name='datprof_provinsi')
    namadata = models.ForeignKey(NamaData, on_delete=models.CASCADE, db_column='namadata_id', related_name='datprof_namadata')
    tahun = models.IntegerField()
    jumlah = models.FloatField()

    class Meta:
        db_table = 'data_provinces'
        verbose_name = 'Data Profil'
        verbose_name_plural = 'Data Profil'

    def __str__(self):
        return f"{self.provinsi.name} - {self.namadata.nama} ({self.tahun})"


class AuditLog(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=[
        ('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete')
    ])
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Log'

    def __str__(self):
        return f"{self.action} {self.model_name} ({self.object_id}) by {self.user}"
        