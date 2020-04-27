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
import argparse
import importlib
import shutil
from operator import itemgetter
from pathlib import Path
from django.utils.text import slugify
from datetime import datetime



logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)



parser = argparse.ArgumentParser()
parser.add_argument(
	"--noop",
	default=False,
	action="store_true",
)
parser.add_argument(
	"--json",
	required=True,
	help="Path to the JSON files",
)
parser.add_argument(
	"--screenshots",
	help="Path to the directory containing screenshots",
)

options = parser.parse_args()

make_files = not options.noop



settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
try:
	settings = importlib.import_module(settings_module)
except ImportError:
	log.error('Could not import settings')
	exit(1)




author_packages = {}
author_names = {}

tag_packages = {}
tag_names = {}

taggit_tag_names = {}

all_screenshots = []

package_list = []

package_pk = 0

SRC_DIR = Path(options.json).resolve()
BASE_DIR = SRC_DIR.parent
# MEDIA_DIR = Path(BASE_DIR.joinpath('media'))
# MEDIA_DIR = Path('/srv/www/quaddicted/media')
MEDIA_DIR = Path(settings.MEDIA_ROOT)

if options.screenshots is not None:
	SS_DIR = Path(options.screenshots)
else:
	SS_DIR = None



#
# Read in ratings
#
ratings = []
ratings_raw = {}
with open(SRC_DIR / 'ratings.json', 'r') as fp:
	ratings_json = json.load(fp)

log.debug("Read %s ratings" % len(ratings_json))

for rating in ratings_json:
	ratings_raw.setdefault(rating['zipname'], []).append({
		'datetime': (datetime.fromtimestamp(rating['timestamp'])).isoformat() + 'Z',
		'score': rating['rating_value'],
		'username': rating['username'],
	})

log.debug("Found ratings for %s packages" % len(ratings_raw.keys()))



map_details = {}
with open(SRC_DIR / 'maps.json', 'r') as fp:
	map_json = json.load(fp)

for m in map_json:
	map_details[m['zipname']] = m


#
# Process the packages/maps
#
rating_pk = 0
for root, dirs, files in os.walk(SRC_DIR / 'json'):
	for file in files:
		if file.endswith('.json'):
			package_pk += 1

			with open(os.path.join(root, file)) as fp:
				j = json.load(fp)

			fields = {
				'uploaded_by': 1,
				'published': True,
			}

			for tag in j['tags']:
				tag_name, tag_value = tag.split('=', 1)

				tag_name = tag_name.strip()
				tag_value = tag_value.strip()

				if tag_name == 'title':
					fields['name'] = tag_value
					continue

				if tag_name == 'releasedate':
					fields['created'] = tag_value
					fields['uploaded_on'] = tag_value
					continue

				if tag_name == 'author':
					author_slug = slugify(tag_value)
					author_name = tag_value

					if author_slug in author_names:
						if author_name != author_names[author_slug]:
							log.warning("Created duplicate author slug: (%s: %s) (%s: %s)" % (author_slug, author_name, author_slug, author_names[author_slug]))
					else:
						author_names[author_slug] = author_name

					author_packages.setdefault(author_slug, []).append(package_pk)
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
			fields['description'] = map_details[package_abs_path.stem]['description']


			if make_files:
				package_abs_path.parent.mkdir(parents=True, exist_ok=True)
				package_abs_path.touch()
			else:
				log.debug(f'Would have created directory {package_abs_path.parent}')
				log.debug(f'Would have touched file {package_abs_path}')


			if SS_DIR is not None:
				screenshot_src_path = SS_DIR / (package_abs_path.stem + '.jpg')

				# print('screenshot_src_path: %s' % screenshot_src_path)
				# print('screenshot_abs_path: %s' % screenshot_abs_path)
				if screenshot_src_path.exists():
					# screenshot_abs_path.symlink_to(screenshot_src_path)
					if make_files:
						shutil.copy(screenshot_src_path, screenshot_abs_path)

						all_screenshots.append({
							'image': str(screenshot_abs_path.relative_to(MEDIA_DIR)),
							'package': package_pk,
						})
					else:
						log.debug(f'Would have copied file {screenshot_src_path} to {screenshot_abs_path}')


			package_list.append({
				'model': 'quaddicted_packages.package',
				'pk': package_pk,
				'fields': fields
			})

			# Create ratings
			try:
				package_ratings = ratings_raw[package_abs_path.stem]
			except KeyError:
				log.warning('No package for rating %s' % package_abs_path.stem)
			else:
				for rating in package_ratings:
					rating_pk += 1

					if rating_pk == 2997:
						log.debug(rating)

					ratings.append({
						'model': 'quaddicted_packages.rating',
						'pk': rating_pk,
						'fields': {
							'username': rating['username'],
							'package': package_pk,
							'score': rating['score'],
							'created': rating['datetime'],
						}
					})

				del(ratings_raw[package_abs_path.stem])

# The left-over ratings; the package has been deleted
log.debug(ratings_raw)

print(yaml.dump(package_list))
print(yaml.dump(ratings))

package_tag_pk = 0
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
		package_tag_pk += 1
		print(yaml.dump([{
			'model': 'taggit.taggeditem',
			'pk': package_tag_pk,
			'fields': {
				'tag': pk,
				'content_type': ['quaddicted_packages', 'package'],
				'object_id': package_id,
			}
		}]))


package_author_pk = 0
for pk, (author_slug, author_name) in enumerate(author_names.items()):
	print(yaml.dump([{
		'model': 'quaddicted_packages.author',
		'pk': pk,
		'fields': {
			'slug': author_slug,
			'name': author_name,
			# 'packages': author_packages[author_slug]
		}
	}]))

	for package_id in author_packages[author_slug]:
		package_author_pk += 1
		print(yaml.dump([{
			'model': 'quaddicted_packages.packageauthors',
			'pk': package_author_pk,
			'fields': {
				'tag': pk,
				'content_type': ['quaddicted_packages', 'package'],
				'object_id': package_id,
			}
		}]))


for pk, screenshot in enumerate(all_screenshots):
	print(yaml.dump([{
		'model': 'quaddicted_packages.screenshot',
		'pk': pk,
		'fields': screenshot,
	}]))
