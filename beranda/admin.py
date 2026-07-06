from django.contrib import admin
from .models import Provinsi, KabupatenJabar

@admin.register(Provinsi)
class ProvinsiAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'alt_name', 'latitude', 'longitude')
    search_fields = ('name', 'alt_name')

@admin.register(KabupatenJabar)
class KabupatenJabarAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama_kabupaten', 'kemiskinan_persen', 'kepadatan_penduduk', 'ipm')
    search_fields = ('nama_kabupaten',)