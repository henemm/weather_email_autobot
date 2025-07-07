import json

with open('data/osm_massifs_corse.geojson') as f:
    data = json.load(f)

names = set()
for el in data['elements']:
    if 'tags' in el and 'name' in el['tags']:
        names.add(el['tags']['name'])

for name in sorted(names):
    print(name) 