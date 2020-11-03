import os
import sys
import re
import json
import logging
import argparse
import importlib
import shutil
from operator import itemgetter
from django.utils.text import slugify
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timezone
import sqlite3
from pprint import pprint



logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


#
# DJANGO_SETTINGS_MODULE=quaddicted.settings.development python ./db_to_fixtures.py
#

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
try:
	settings = importlib.import_module(settings_module)
except ImportError:
	log.error('Could not import settings')
	exit(1)

MEDIA_DIR = os.path.abspath(settings.MEDIA_ROOT)

# if options.screenshots is not None:
# 	SCREENSHOT_DIR = os.path.abspath(options.screenshots)
# else:
# 	SCREENSHOT_DIR = None


#
# Current pk is the zipname
#
pk_from_zip = {}

#
# Get the SHA256 hash from the JSON files
#
hash_from_zip = {}
for current_dir, dirs, files in os.walk(os.path.join(SCRIPT_DIR, "json")):
	for file in files:
		if file.endswith(".json"):
			with open(os.path.join(current_dir, file), "r") as fp:
				j = json.load(fp)

			zipname = os.path.splitext(j['filename'][0])[0]
			hash_from_zip[zipname] = j['sha256']

#
# Create fixtures from the old database
#
fixtures = [] # all fixtures
authors = {} # temporary storage to extracting authors
package_urls = [] # urls that were in the map table
with sqlite3.connect(os.path.join(SCRIPT_DIR, 'quaddicted.sqlite')) as con:
	con.row_factory = sqlite3.Row
	c = con.cursor()

	screenshot_pk = 1
	for r in c.execute("""SELECT id,
	                             author,
	                             commandline,
	                             date,
	                             description,
	                             size,
	                             timestamp,
	                             title,
	                             type,
	                             url,
	                             zipbasedir,
	                             zipname
	                      FROM maps"""):
		package_pk = r['id']
		zipname = r['zipname']
		sha256hash = hash_from_zip.get(zipname, "")
		pk_from_zip[zipname] = package_pk

		# quaddicted_packages.package
		fixtures.append({
			"pk": package_pk,
			"model": "quaddicted_packages.package",
			"fields": {
				"base_dir": r['zipbasedir'],
				"command_line": r['commandline'],
				"created": (datetime.strptime(r['date'], "%d.%m.%Y")).replace(tzinfo=timezone.utc),
				"description": r['description'],
				"file": "packages/{}/{}/{}.zip".format(sha256hash[0], sha256hash, zipname),
				"file_hash": sha256hash,
				"file_name": zipname + ".zip",
				"file_size": r['size'],
				"game": "q1",
				"name": r['title'],
				"published": True, # publish them all
				"type": r['type'],
				"uploaded_by": 1, # uploaded by the admin
				"uploaded_on": datetime.fromtimestamp(r['timestamp'], timezone.utc),
			}
		})

		#
		# PackageUrl Homepage
		#
		if r['url']:
			package_urls.append({
				"name": "Homepage",
				"url": r['url'],
				"package": package_pk,
			})

		#
		# PackageScreenshot
		#
		screenshot_path = "packages/{}/{}/{}.jpg".format(sha256hash[0], sha256hash, zipname)
		if os.path.exists(os.path.join(MEDIA_DIR, screenshot_path)):
			fixtures.append({
				"pk": screenshot_pk,
				"model": "quaddicted_packages.packagescreenshot",
				"fields": {
					"image": "packages/{}/{}/{}.jpg".format(sha256hash[0], sha256hash, zipname),
					"package": package_pk,
				}
			})
			screenshot_pk += 1

		#
		# PackageAuthor
		#
		# split the author list and make proper records
		for name in re.split(",|&amp;", r['author']):
			name = name.strip()
			author_slug = slugify(name)
			author_name = name

			if author_slug in authors.keys():
				authors[author_slug]['packages'].add(package_pk)
			else:
				authors[author_slug] = {
					"name": author_name,
					"packages": set([package_pk])
				}

	#
	# PackageAuthor
	#
	author_pk = 1
	author_pkg_pk = 1
	for author_slug, author in authors.items():
		fixtures.append({
			"pk": author_pk,
			"model": "quaddicted_packages.packageauthor",
			"fields": {
				"slug": author_slug,
				"name": author['name'],
			}
		})

		for pkg_pk in author['packages']:
			fixtures.append({
				"pk": author_pkg_pk,
				"model": "quaddicted_packages.package_authors",
				"fields": {
					"package": pkg_pk,
					"packageauthor": author_pk,
				}
			})
			author_pkg_pk += 1
		author_pk += 1

	#
	# PackageUrl
	#
	url_pk = 1
	# process the URLs embedded into the map table
	for url_fields in package_urls:
		fixtures.append({
			"pk": url_pk,
			"model": "quaddicted_packages.packageurl",
			"fields": url_fields
		})
		url_pk += 1
	# process the external links
	for r in c.execute("""SELECT zipname,
	                             title,
	                             url
	                      FROM externallinks"""):
		try:
			package_pk = pk_from_zip[r['zipname']]
		except KeyError:
			continue
		else:
			fixtures.append({
				"pk": url_pk,
				"model": "quaddicted_packages.packageurl",
				"fields": {
					"name": r['title'],
					"url": r['url'],
					"package": package_pk,
				}
			})
		url_pk += 1

	#
	# PackageRating
	#
	rating_pk = 1
	ratings = set()
	for r in c.execute("""SELECT timestamp,
	                             zipname,
	                             rating_value,
	                             username
	                      FROM ratings"""):
		try:
			package_pk = pk_from_zip[r['zipname']]
		except KeyError:
			continue
		else:
			# Original database has bad data and duplicate entries
			if (r['username'], r['zipname']) in ratings:
				# print((r['username'], r['zipname']))
				continue

			ratings.add((r['username'], r['zipname']))
			fixtures.append({
				"pk": rating_pk,
				"model": "quaddicted_packages.packagerating",
				"fields": {
					"created": datetime.fromtimestamp(r['timestamp'], timezone.utc),
					"package": package_pk,
					"score": r['rating_value'],
					"username": r['username'],
				}
			})
		rating_pk += 1

	#
	# Tags
	#
	tags = {}
	for r in c.execute("""SELECT zipname, tag
	                      FROM tags"""):
		try:
			package_pk = pk_from_zip[r['zipname']]
		except KeyError:
			continue
		else:
			tag_slug = slugify(r['tag'])

			if tag_slug in tags.keys():
				tags[tag_slug]['packages'].add(package_pk)
			else:
				tags[tag_slug] = {
					"name": r['tag'],
					"packages": set([package_pk])
				}
	tag_pk = 1
	taggeditem_pk = 1
	for slug, tag in tags.items():
		fixtures.append({
			"pk": tag_pk,
			"model": "taggit.tag",
			"fields": {
				"name": tag['name'],
				"slug": slug,
			}
		})
		for pkg_pk in tag['packages']:
			fixtures.append({
				"pk": taggeditem_pk,
				"model": "taggit.taggeditem",
				"fields": {
					"content_type": ["quaddicted_packages", "package"],
					"object_id": pkg_pk,
					"tag": tag_pk,
				}
			})
			taggeditem_pk += 1
		tag_pk += 1


	#
	# PackageFile
	#
	file_pk = 1
	for r in c.execute("""SELECT zipname,
	                             size,
	                             date,
	                             filename
	                      FROM includedfiles"""):
		try:
			package_pk = pk_from_zip[r['zipname']]
		except KeyError:
			continue
		else:
			fixtures.append({
				"pk": file_pk,
				"model": "quaddicted_packages.packagefile",
				"fields": {
					"name": r['filename'],
					"last_modified": (datetime.strptime(r['date'].strip(), "%d.%m.%Y")).replace(tzinfo=timezone.utc),
					"size": r['size'],
					"package": package_pk,
				}
			})
		file_pk += 1

	#
	# PackageScreenshot
	#

	#
	# package_dependencies
	#
	dependency_pk = 1
	for r in c.execute("""SELECT zipname, dependency FROM dependencies"""):
		try:
			from_package_pk = pk_from_zip[r['zipname']]
			to_package_pk = pk_from_zip[r['dependency']]
		except KeyError:
			continue
		else:
			fixtures.append({
				"pk": dependency_pk,
				"model": "quaddicted_packages.package_dependencies",
				"fields": {
					"from_package_id": from_package_pk,
					"to_package_id": to_package_pk,
				}
			})
		dependency_pk += 1


# json.dumps(fixtures)
print(json.dumps(fixtures,
                 sort_keys=True,
                 indent=8,
                 cls=DjangoJSONEncoder))
