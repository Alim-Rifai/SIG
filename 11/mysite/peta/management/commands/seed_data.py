"""
Management command to seed NamaData and Datprof with sample statistical data.
Creates sample data categories and random statistical values per province per year.
"""

import random

from django.core.management.base import BaseCommand

from peta.models import Provinsi, NamaData, Datprof


# Sample data categories (nama data statistik)
NAMA_DATA_LIST = [
    'Kepadatan Penduduk (jiwa/km²)',
    'Jumlah Penduduk (ribu jiwa)',
    'Luas Wilayah (km²)',
    'Indeks Pembangunan Manusia',
    'Tingkat Pengangguran (%)',
    'PDRB per Kapita (juta Rp)',
    'Angka Harapan Hidup (tahun)',
    'Rata-rata Lama Sekolah (tahun)',
]

# Approximate real data ranges per category
DATA_RANGES = {
    'Kepadatan Penduduk (jiwa/km²)': (10, 15000),
    'Jumlah Penduduk (ribu jiwa)': (500, 50000),
    'Luas Wilayah (km²)': (600, 320000),
    'Indeks Pembangunan Manusia': (55, 82),
    'Tingkat Pengangguran (%)': (1.5, 12.0),
    'PDRB per Kapita (juta Rp)': (15, 250),
    'Angka Harapan Hidup (tahun)': (62, 75),
    'Rata-rata Lama Sekolah (tahun)': (5, 12),
}

YEARS = [2021, 2022, 2023, 2024]


class Command(BaseCommand):
    help = 'Seed NamaData and Datprof tables with sample statistical data'

    def handle(self, *args, **options):
        provinces = list(Provinsi.objects.all())
        if not provinces:
            self.stderr.write(self.style.ERROR(
                'No provinces found. Run import_provinces first.'
            ))
            return

        # Create NamaData entries
        nama_data_objects = []
        for nama in NAMA_DATA_LIST:
            obj, created = NamaData.objects.get_or_create(nama=nama)
            nama_data_objects.append(obj)
            if created:
                self.stdout.write(f'  Created NamaData: {nama}')

        # Create Datprof entries for each province × nama_data × year
        created_count = 0
        for nd in nama_data_objects:
            min_val, max_val = DATA_RANGES.get(nd.nama, (10, 1000))
            for year in YEARS:
                for prov in provinces:
                    _, created = Datprof.objects.get_or_create(
                        provinsi=prov,
                        namadata=nd,
                        tahun=year,
                        defaults={
                            'jumlah': round(random.uniform(min_val, max_val), 2)
                        }
                    )
                    if created:
                        created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! NamaData: {len(nama_data_objects)}, '
            f'Datprof records created: {created_count}, '
            f'Total Datprof: {Datprof.objects.count()}'
        ))
