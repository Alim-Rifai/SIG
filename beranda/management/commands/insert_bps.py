from django.core.management.base import BaseCommand
from beranda.models import KabupatenJabar, Provinsi

class Command(BaseCommand):
    help = 'Menginput semua data BPS Jawa Barat sekaligus ke database'

    def handle(self, *args, **options):
        # Data asli dari tabel BPS kelompokmu
        data_bps = {
            "BOGOR": {"kepadatan": 1852.78, "ipm": 73.63, "miskin": 7.05},
            "SUKABUMI": {"kepadatan": 618.34, "ipm": 70.18, "miskin": 6.87},
            "CIANJUR": {"kepadatan": 702.15, "ipm": 68.89, "miskin": 10.14},
            "BANDUNG": {"kepadatan": 2125.4, "ipm": 74.59, "miskin": 6.19},
            "GARUT": {"kepadatan": 842.1, "ipm": 69.91, "miskin": 9.68},
            "TASIKMALAYA": {"kepadatan": 704.12, "ipm": 69.98, "miskin": 10.23},
            "CIAMIS": {"kepadatan": 852.4, "ipm": 73.64, "miskin": 7.39},
            "KUNINGAN": {"kepadatan": 948.15, "ipm": 71.56, "miskin": 11.88},
            "CIREBON": {"kepadatan": 2250.6, "ipm": 72.3, "miskin": 11.0},
            "MAJALENGKA": {"kepadatan": 1045.3, "ipm": 71.37, "miskin": 10.82},
            "SUMEDANG": {"kepadatan": 742.9, "ipm": 74.57, "miskin": 9.1},
            "INDRAMAYU": {"kepadatan": 874.2, "ipm": 70.72, "miskin": 11.93},
            "SUBANG": {"kepadatan": 794.3, "ipm": 72.05, "miskin": 9.49},
            "PURWAKARTA": {"kepadatan": 1042.5, "ipm": 73.99, "miskin": 8.41},
            "KARAWANG": {"kepadatan": 1345.2, "ipm": 73.82, "miskin": 7.86},
            "BEKASI": {"kepadatan": 1485.6, "ipm": 76.8, "miskin": 4.8},
            "BANDUNG BARAT": {"kepadatan": 1344.2, "ipm": 70.77, "miskin": 10.49},
            "PANGANDARAN": {"kepadatan": 425.1, "ipm": 71.03, "miskin": 8.75},
            "KOTA BOGOR": {"kepadatan": 9452.1, "ipm": 79.03, "miskin": 6.53},
            "KOTA SUKABUMI": {"kepadatan": 7420.3, "ipm": 77.69, "miskin": 7.2},
            "KOTA BANDUNG": {"kepadatan": 15124.5, "ipm": 83.75, "miskin": 3.87},
            "KOTA CIREBON": {"kepadatan": 9104.2, "ipm": 78.09, "miskin": 9.02},
            "KOTA BEKASI": {"kepadatan": 13420.6, "ipm": 83.55, "miskin": 4.01},
            "KOTA DEPOK": {"kepadatan": 10425.8, "ipm": 83.05, "miskin": 2.34},
            "KOTA CIMAHI": {"kepadatan": 13540.1, "ipm": 80.3, "miskin": 4.39},
            "KOTA TASIKMALAYA": {"kepadatan": 4210.4, "ipm": 76.03, "miskin": 11.1},
            "KOTA BANJAR": {"kepadatan": 1845.2, "ipm": 75.01, "miskin": 5.85}
        }

        # Bersihkan data kabupaten lama dulu biar gak bentrok FK-nya
        # (Gunakan try-except biar kalau tabel kosong gak ikutan error)
        try:
            KabupatenJabar.objects.all().delete()
            Provinsi.objects.all().delete()
        except:
            pass

        # 1. PAKSA INPUT PROVINSI DENGAN ID MANUAL = 1
        provinsi_obj = Provinsi.objects.create(
            id=1,
            name="JAWA BARAT"
        )

        # 2. INPUT OTOMATIS KABUPATEN NEMPEL KE PROVINSI ID 1
        for index, (nama_kota, detail) in enumerate(data_bps.items(), start=1):
            KabupatenJabar.objects.create(
                id=index,
                nama_kabupaten=nama_kota,
                kemiskinan_persen=detail["miskin"],
                kepadatan_penduduk=detail["kepadatan"],
                ipm=detail["ipm"],
                provinsi=provinsi_obj
            )
            
        self.stdout.write(self.style.SUCCESS('🔥 BERHASIL TOTAL! 27 Data Sukses Masuk Database Anda!'))
        