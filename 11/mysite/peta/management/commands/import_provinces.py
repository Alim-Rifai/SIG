"""
Management command to import province data from GeoJSON files into the database.
Reads individual province GeoJSON files from static/geojson/province/ and creates
Provinsi records with id, name, latitude, and longitude.
"""

import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from peta.models import Provinsi


class Command(BaseCommand):
    help = 'Import province data from GeoJSON files into the Provinsi table'

    def handle(self, *args, **options):
        geojson_dir = os.path.join(settings.BASE_DIR, 'static', 'geojson', 'province')
        files = sorted([
            f for f in os.listdir(geojson_dir)
            if f.endswith('.geojson') and f != 'all-provinces.geojson'
        ])

        if not files:
            self.stderr.write(self.style.ERROR(f'No GeoJSON files found in {geojson_dir}'))
            return

        created_count = 0
        updated_count = 0

        for filename in files:
            province_id = int(os.path.splitext(filename)[0])
            filepath = os.path.join(geojson_dir, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                features = data.get('features', [])
                if not features:
                    self.stderr.write(f'  Skipping {filename}: no features')
                    continue

                props = features[0].get('properties', {})
                name = props.get('name', props.get('NAME_1', props.get('PROPNAME', f'Province {province_id}')))
                latitude = props.get('latitude', 0.0)
                longitude = props.get('longitude', 0.0)

                obj, created = Provinsi.objects.update_or_create(
                    id=province_id,
                    defaults={
                        'name': name,
                        'alt_name': name,
                        'latitude': latitude,
                        'longitude': longitude,
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except (json.JSONDecodeError, IOError) as e:
                self.stderr.write(f'  Error processing {filename}: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created: {created_count}, Updated: {updated_count}, Total: {created_count + updated_count}'
        ))
