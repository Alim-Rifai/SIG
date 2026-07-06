"""
Script to merge individual province GeoJSON files into a single combined file.

Reads all .geojson files from static/geojson/province/ (excluding all-provinces.geojson),
extracts features, adds province_id property based on filename, and writes a combined
FeatureCollection to static/geojson/province/all-provinces.geojson.
"""

import json
import os
import sys


def merge_province_geojson(input_dir, output_file):
    """
    Merge individual province GeoJSON files into a single FeatureCollection.

    Args:
        input_dir: Path to directory containing individual province .geojson files
        output_file: Path to write the combined GeoJSON file
    """
    all_features = []
    errors = []
    processed = 0

    # Get all .geojson files, excluding the output file itself
    output_basename = os.path.basename(output_file)
    geojson_files = sorted([
        f for f in os.listdir(input_dir)
        if f.endswith('.geojson') and f != output_basename
    ])

    if not geojson_files:
        print(f"No GeoJSON files found in {input_dir}")
        sys.exit(1)

    print(f"Found {len(geojson_files)} province GeoJSON files to merge.")

    for filename in geojson_files:
        filepath = os.path.join(input_dir, filename)
        province_id = os.path.splitext(filename)[0]  # e.g., "11" from "11.geojson"

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get('type') != 'FeatureCollection':
                errors.append(f"  - {filename}: Not a FeatureCollection (type: {data.get('type')})")
                continue

            features = data.get('features', [])
            if not features:
                errors.append(f"  - {filename}: No features found")
                continue

            for feature in features:
                # Ensure properties dict exists
                if feature.get('properties') is None:
                    feature['properties'] = {}

                # Add province_id property for identification
                feature['properties']['province_id'] = province_id

                all_features.append(feature)

            processed += 1

        except json.JSONDecodeError as e:
            errors.append(f"  - {filename}: Invalid JSON - {e}")
        except IOError as e:
            errors.append(f"  - {filename}: Read error - {e}")

    # Build combined FeatureCollection
    combined = {
        "type": "FeatureCollection",
        "features": all_features
    }

    # Write output file without indentation to keep file size manageable
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False)

    print(f"\nMerge complete:")
    print(f"  - Files processed: {processed}/{len(geojson_files)}")
    print(f"  - Total features: {len(all_features)}")
    print(f"  - Output: {output_file}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for err in errors:
            print(err)

    return len(errors) == 0


if __name__ == '__main__':
    # Resolve paths relative to this script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, 'static', 'geojson', 'province')
    output_file = os.path.join(input_dir, 'all-provinces.geojson')

    success = merge_province_geojson(input_dir, output_file)
    sys.exit(0 if success else 1)
