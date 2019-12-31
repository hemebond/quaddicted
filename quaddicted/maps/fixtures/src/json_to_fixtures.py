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

all_screenshots = []

map_list = []

map_pk = 0

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MEDIA_DIR = Path(BASE_DIR.joinpath('media'))

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

			# Fixtures for map packages require
			# actual files so here we create dummy files
			# e.g., /home/james/Workspace/quaddicted/quaddicted/media/maps/by-sha256/6/6e42a183c0e1992069f53e235285eb3863d4d7fc33f0eb584f262223e174a381/dopa.zip
			package_abs_path = MEDIA_DIR.joinpath('maps',
			                                      'by-sha256',
			                                      j['sha256'][0],
			                                      j['sha256'],
			                                      j['filename'][0])
			# /home/james/Workspace/quaddicted/quaddicted/media/maps/by-sha256/6/6e42a183c0e1992069f53e235285eb3863d4d7fc33f0eb584f262223e174a381/dopa.jpg
			screenshot_abs_path = package_abs_path.parent.joinpath(package_abs_path.stem + '.jpg')

			all_packages.append({
				'file': str(package_abs_path.relative_to(MEDIA_DIR)),
				'file_name': j['filename'][0],
				'file_hash': j['sha256'],
				'created': fields['created'],
				'map': map_pk,
			})
			package_abs_path.parent.mkdir(parents=True, exist_ok=True)
			package_abs_path.touch()

			screenshot_src_path = BASE_DIR.joinpath(
				'maps',
				'fixtures',
				'screenshots',
				package_abs_path.stem + '.jpg'
			)

			# print('screenshot_src_path: %s' % screenshot_src_path)
			# print('screenshot_abs_path: %s' % screenshot_abs_path)
			if screenshot_src_path.exists():
				if not screenshot_abs_path.exists():
					screenshot_abs_path.symlink_to(screenshot_src_path)

				all_screenshots.append({
					'image': str(screenshot_abs_path.relative_to(MEDIA_DIR)),
					'map': map_pk,
				})

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

for pk, screenshot in enumerate(all_screenshots):
	print(yaml.dump([{
		'model': 'maps.screenshot',
		'pk': pk,
		'fields': screenshot,
	}]))
