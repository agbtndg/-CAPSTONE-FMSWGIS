import os
import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import fromstr
from ...models import Barangay, FloodSusceptibility

class Command(BaseCommand):
    help = 'Loads GeoJSON files into Barangay and FloodSusceptibility models'

    def handle(self, *args, **options):
        data_dir = r"C:\Users\aldri\Documents\SilayDRRMO\maps\data"
        barangay_file = os.path.join(data_dir, 'silay_barangay_map.geojson')
        flood_file = os.path.join(data_dir, 'silay_flood_map.geojson')

        # Load Barangay data
        with open(barangay_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for feature in data['features']:
                props = feature['properties']
                geom = fromstr(json.dumps(feature['geometry']))
                Barangay.objects.update_or_create(
                    id=props['id'],
                    defaults={
                        'name': props['name'],
                        'parent_id': props['parent_id'],
                        'geometry': geom
                    }
                )

        # Load FloodSusceptibility data
        with open(flood_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for feature in data['features']:
                props = feature['properties']
                geom = fromstr(json.dumps(feature['geometry']))
                FloodSusceptibility.objects.update_or_create(
                    lgu=props.get('LGU', 'Silay City'),
                    psgc_lgu=props.get('PSGC_LGU', '64526000'),
                    haz_class=props.get('HazClass', 'Flooding'),
                    haz_code=props.get('HazCode', 'LF'),  # Default to LF if missing
                    haz_area_ha=props.get('HazArea_Ha', 0.0),
                    defaults={
                        'geometry': geom
                    }
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded shapefiles'))