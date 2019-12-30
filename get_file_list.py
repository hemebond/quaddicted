import os
import io
import hashlib
from zipfile import ZipFile, BadZipFile
from datetime import datetime
from vgio.quake.pak import PakFile, BadPakFile  # https://github.com/joshuaskelly/vgio/ <3
from typing import Union, BinaryIO

def get_digest(b):
	"""Calculate the SHA256 hash of the bytes"""
	# via https://stackoverflow.com/a/55542529/4828720
	h = hashlib.sha256()

	while True:
		# Reading is buffered, so we can read smaller chunks.
		chunk = b.read(h.block_size)
		if not chunk:
			break
		h.update(chunk)

	return h.hexdigest()

def files_in_archive(archive_file: Union[str, BinaryIO], hashed: bool=True, recursive: bool=True) -> dict:
	"""
	Read a .pak or .zip file and return a dict of information about the files inside

	e.g.:
	{
		'readme.txt': {
			'size': 3206,
			'timestamp': '2014-08-15T17:51:54.000Z',
			'sha256': '0a8dbd908c23e3d7a665ee30af4e38eaecb83b5a326b051c64883078d23b2251'
		}
	}

	:param archive_file: Either the path to the file, or a file-like object
	:type archive_file: str or BinaryIO
	:param bool hashed: include a sha256 hash of each file
	:param bool recursive: recurse into any file archives contained inside
	"""
	try:
		archive = PakFile(archive_file)
	except BadPakFile:
		archive = ZipFile(archive_file)

	files = {}

	for file_path in archive.namelist():
		file = archive.getinfo(file_path)

		files[file_path] = {}
		files[file_path]['size'] = file.file_size

		if hasattr(file, 'date_time'):
			files[file_path]['timestamp'] = datetime.strftime(datetime(*file.date_time), "%Y-%m-%dT%H:%M:%S.000Z")

		if hashed or recursive:
			with archive.open(file_path) as f:
				if hashed:
					files[file_path]['sha256'] = get_digest(f)

				file_name, file_ext = os.path.splitext(file_path)

				if recursive and file_ext in ['.zip', '.pak']:
					files[file_path]['files'] = files_in_archive(f, hashed=hashed, recursive=recursive)

	archive.close()

	return files


def files_in_pak(pak_path, hashed=True):
	"""TODO docstring"""

	files = {}

	with PakFile(pak_path) as pak_file:
		# pak_file == vgio.quake.pak.PakFile
		for file_path in pak_file.namelist():
			# file == vgio.quake.pak.PakInfo
			files[file_path] = get_file_info(pak_file, file_path, hashed=hashed)
	return files


def files_in_zip(zip_path, hashed=True, recursive=True):
	"""TODO docstring"""

	files = {}

	with ZipFile(zip_path) as zip_file:
		# zip_file == ZipFile
		print(zip_file)

		for file_path in zip_file.namelist():
			# file == ZipInfo
			files[file_path] = get_file_info(zip_file, file_path, hashed=hashed)

			if recursive:
				with zip_file.open(file_path) as f:
					file_name, file_ext = os.path.splitext(file_path)

					if recursive:
						if file_ext == ".pak":
							files[file_path]['files'] = files_in_pak(f, hashed=hashed)
						if file_ext == ".zip":
							files[file_path]['files'] = files_in_zip(f, hashed=hashed, recursive=recursive)
	return files


def old_files_in_archive(archive_path, hashed=True, recursive=True):
	if archive_path[-4:] == '.zip':
		return files_in_zip(archive_path, hashed=hashed, recursive=recursive)

	if archive_path[-4:] == '.pak':
		return files_in_pak(archive_path, hashed=hashed)



file = "/home/james/Downloads/1000cuts1a.zip"
# file = "/home/james/.darkplaces/bbelief/pak0.pak"

files = files_in_archive(file)

# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(files)
print(files)
