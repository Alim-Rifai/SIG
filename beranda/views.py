from django.shortcuts import render
from beranda.models import KabupatenJabar
import json

def halaman_peta(request):
    # Ambil semua data dari database admin
    data_db = KabupatenJabar.objects.all()
    
    # Bungkus ke dalam format dictionary/json agar mudah dibaca JavaScript
    bps_dict = {}
    for item in data_db:
        nama_key = item.nama_kabupaten.upper().strip()
        bps_dict[nama_key] = {
            "miskin": float(item.kemiskinan_persen),
            "kepadatan": float(item.kepadatan_penduduk),
            "ipm": float(item.ipm)
        }
        
    context = {
        'data_bps_json': json.dumps(bps_dict)
    }
    
    # --- GANTI DI SINI JADI peta.html ---
    # Jika file peta.html ada di dalam folder templates/beranda/, ubah jadi 'beranda/peta.html'
    return render(request, 'peta.html', context)