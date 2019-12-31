import os
import json
import yaml
from pathlib import Path

all_authors = {
	# name: [maps...]
}
all_tags = {
	# name: [maps...]
}

all_packages = [
	# file
	# file_name
	# file_hash
	# created
	# map
]

map_list = []

map_pk = 0

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

for root, dirs, files in os.walk('.'):
	for file in files:
		if file.endswith('.json'):
			map_pk += 1

			with open(os.path.join(root, file)) as fp:
				j = json.load(fp)

			fields = {
			}

			for tag in j['tags']:
				tag_name, tag_value = tag.split('=', 1)

				if tag_name == 'title':
					fields['name'] = tag_value
					continue

				if tag_name == 'releasedate':
					fields['created'] = tag_value
					continue

				if tag_name == 'author':
					all_authors.setdefault(tag_value, []).append(map_pk)
					continue

				if tag_name == 'tag':
					all_tags.setdefault(tag_value, []).append(map_pk)
					continue

				if tag_name == 'game':
					fields['game'] = {
						'quake': 'q1',
					}.get(tag_value, 'q4')
					continue

			package_file_path = os.path.join('maps',
			                                 'by-sha256',
			                                 j['sha256'][0],
			                                 j['sha256'],
			                                 j['filename'][0])
			all_packages.append({
				'file': package_file_path,
				'file_name': j['filename'][0],
				'file_hash': j['sha256'],
				'created': fields['created'],
				'map': map_pk,
			})

			Path(os.path.dirname(os.path.join(BASE_DIR, 'media', package_file_path))).mkdir(parents=True, exist_ok=True)
			Path(os.path.join(BASE_DIR, 'media', package_file_path)).touch()

			map_list.append({
				'model': 'maps.map',
				'pk': map_pk,
				'fields': fields
			})

print(yaml.dump(map_list))

for pk, (tag_name, tag_maps) in enumerate(all_tags.items()):
	print(yaml.dump([{
		'model': 'maps.tag',
		'pk': pk,
		'fields': {
			'name': tag_name,
			'maps': tag_maps
		}
	}]))

# print(all_tags)

for pk, (author_name, author_maps) in enumerate(all_authors.items()):
	print(yaml.dump([{
		'model': 'maps.author',
		'pk': pk,
		'fields': {
			'name': author_name,
			'maps': author_maps
		}
	}]))
# print(all_authors)

for pk, package in enumerate(all_packages):
	print(yaml.dump([{
		'model': 'maps.mappackage',
		'pk': pk,
		'fields': package,
	}]))
