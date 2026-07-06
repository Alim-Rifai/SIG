import json

from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from .models import Provinsi, Kabkota, Kecamatan, NamaData, Datprof
from .validators import validate_form_params


@staff_member_required
def admin_dashboard(request):
    context = {
        'provinsi_count': Provinsi.objects.count(),
        'kabkota_count': Kabkota.objects.count(),
        'kecamatan_count': Kecamatan.objects.count(),
        'datprof_count': Datprof.objects.count(),
    }
    return render(request, 'admin/dashboard.html', context)


def index(request):
    return render(request, 'index.html')


def peta(request):
    # Cached province list
    semua_provinsi = cache.get('province_list')
    if semua_provinsi is None:
        semua_provinsi = list(Provinsi.objects.all().order_by('id'))
        cache.set('province_list', semua_provinsi, 300)

    all_data_names = NamaData.objects.all()

    selected_data_id = request.GET.get('data_id')
    selected_year = request.GET.get('tahun')

    stat_data = []
    sub_judul_kecil = ""

    # Validate parameters if both are provided
    if selected_data_id and selected_year:
        errors = validate_form_params(selected_data_id, selected_year)
        if errors:
            return JsonResponse({
                'status': 'error',
                'errors': [{'field': k, 'message': v} for k, v in errors.items()]
            }, status=400)

        data_name_obj = NamaData.objects.get(id=selected_data_id)
        sub_judul_kecil = f"({data_name_obj.nama} Tahun {selected_year})"

        records = Datprof.objects.filter(namadata_id=selected_data_id, tahun=selected_year)
        for r in records:
            stat_data.append({
                'prov_name': r.provinsi.name,
                'latitude': r.provinsi.latitude,
                'longitude': r.provinsi.longitude,
                'jumlah': r.jumlah
            })

    # Province list as JSON for Select2
    province_list_json = json.dumps([
        {'id': p.id, 'name': p.name, 'latitude': p.latitude, 'longitude': p.longitude}
        for p in semua_provinsi
    ])

    context = {
        'all_data_names': all_data_names,
        'semua_provinsi': semua_provinsi,
        'stat_data': json.dumps(stat_data),
        'province_list_json': province_list_json,
        'sub_judul_kecil': sub_judul_kecil,
    }
    return render(request, 'peta.html', context)