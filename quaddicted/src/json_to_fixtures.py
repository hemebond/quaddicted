"""
└── src
    ├── json
    └── screenshots
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from django.utils.text import slugify


make_files = True
if len(sys.argv) > 1 and sys.argv[1] == '-noop':
	make_files = False


author_packages = {}
author_names = {}

tag_packages = {}
tag_names = {}

all_packages = [
	# file
	# file_name
	# file_hash
	# created
	# map
]

taggit_tag_names = {}

all_screenshots = []

package_list = []

package_pk = 0

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = Path(BASE_DIR.joinpath('media'))

for root, dirs, files in os.walk('.'):
	for file in files:
		if file.endswith('.json'):
			package_pk += 1

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
					author_username = slugify(tag_value)
					author_fullname = tag_value

					if author_username in author_names:
						if author_fullname != author_names[author_username]:
							logging.warning("Created duplicate author username slug: (%s: %s) (%s: %s)" % (author_username, author_fullname, author_username, author_names[author_username]))
					else:
						author_names[author_username] = author_fullname

					author_packages.setdefault(author_username, []).append(package_pk)
					continue

				if tag_name == 'tag':
					# taggit requires unique slugs
					tag_slug = slugify(tag_value)
					tag_packages.setdefault(tag_slug, []).append(package_pk)
					tag_names[tag_slug] = tag_value
					continue

				if tag_name == 'game':
					fields['game'] = {
						'quake': 'q1',
					}.get(tag_value, 'q4')
					continue

			# Fixtures for map packages require
			# actual files so here we create dummy files
			# e.g., /home/james/Workspace/quaddicted/quaddicted/media/packages/6/6e42a183c0e1992069f53e235285eb3863d4d7fc33f0eb584f262223e174a381/dopa.zip
			package_abs_path = MEDIA_DIR.joinpath('packages',
			                                      j['sha256'][0],
			                                      j['sha256'],
			                                      j['filename'][0])
			# /home/james/Workspace/quaddicted/quaddicted/media/packages/6/6e42a183c0e1992069f53e235285eb3863d4d7fc33f0eb584f262223e174a381/dopa.jpg
			screenshot_abs_path = package_abs_path.parent.joinpath(package_abs_path.stem + '.jpg')

			fields['file'] = str(package_abs_path.relative_to(MEDIA_DIR))
			fields['file_name'] = j['filename'][0]
			fields['file_hash'] = j['sha256']

			if make_files:
				package_abs_path.parent.mkdir(parents=True, exist_ok=True)
				package_abs_path.touch()

			screenshot_src_path = BASE_DIR.joinpath(
				'src',
				'screenshots',
				package_abs_path.stem + '.jpg'
			)

			# print('screenshot_src_path: %s' % screenshot_src_path)
			# print('screenshot_abs_path: %s' % screenshot_abs_path)
			if screenshot_src_path.exists():
				if make_files and not screenshot_abs_path.exists():
					screenshot_abs_path.symlink_to(screenshot_src_path)

				all_screenshots.append({
					'image': str(screenshot_abs_path.relative_to(MEDIA_DIR)),
					'package': package_pk,
				})

			package_list.append({
				'model': 'packages.package',
				'pk': package_pk,
				'fields': fields
			})


print(yaml.dump(package_list))


for pk, (tag_slug, tag_maps) in enumerate(tag_packages.items()):
	print(yaml.dump([{
		'model': 'taggit.tag',
		'pk': pk,
		'fields': {
			'name': tag_names[tag_slug],
			'slug': tag_slug,
		}
	}]))

	for package_id in tag_maps:
		print(yaml.dump([{
			'model': 'taggit.taggeditem',
			'pk': None,
			'fields': {
				'tag': pk,
				'content_type': ['packages', 'package'],
				'object_id': package_id,
			}
		}]))


for pk, (author_username, author_fullname) in enumerate(author_names.items()):
	print(yaml.dump([{
		'model': 'packages.author',
		'pk': pk,
		'fields': {
			'username': author_username,
			'fullname': author_fullname,
			'packages': author_packages[author_username]
		}
	}]))


for pk, screenshot in enumerate(all_screenshots):
	print(yaml.dump([{
		'model': 'packages.screenshot',
		'pk': pk,
		'fields': screenshot,
	}]))
