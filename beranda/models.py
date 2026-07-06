from django.db import models

class Provinsi(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    alt_name = models.CharField(max_length=255, default='')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    class Meta:
        db_table = 'provinces'

    def __str__(self):
        return self.name

# Model khusus untuk menampung data 3 peta tematik Jawa Barat kamu
class KabupatenJabar(models.Model):
    id = models.BigIntegerField(primary_key=True)
    provinsi = models.ForeignKey(Provinsi, on_delete=models.CASCADE, default=32) # Kode 32 adalah Jawa Barat
    nama_kabupaten = models.CharField(max_length=255)
    kemiskinan_persen = models.FloatField(help_text="Data dari file Kemiskinan.jpg")
    kepadatan_penduduk = models.IntegerField(help_text="Data dari file kepadatan penduduk Jabar 2024.jpg")
    ipm = models.FloatField(help_text="Data dari file Index Pembangunan Manusia (IPM).jpg")

    class Meta:
        db_table = 'kabupaten_jabar'

    def __str__(self):
        return self.nama_kabupaten