from django.db import models
from django.urls import reverse
from django.utils import timezone

from datetime import datetime

from PIL import Image

import os
import hashlib

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from django.contrib.auth.models import User


# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import post_delete, pre_save
from django.dispatch.dispatcher import receiver


def map_screenshot_path(instance, filename):
	file_ext = os.path.splitext(filename)[1]
	file_dir = instance.get_image_basedir()
	ctx = hashlib.sha256()

	if instance.image.multiple_chunks():
		for data in instance.image.chunks(ctx.block_size):
			ctx.update(data)
	else:
		ctx.update(instance.image.read())

	return os.path.join(file_dir, ctx.hexdigest() + file_ext)


def map_package_path(instance, filename):
	file_dir = instance.get_image_basedir()
	ctx = hashlib.sha256()

	if instance.file.multiple_chunks():
		for data in instance.file.chunks(ctx.block_size):
			ctx.update(data)
	else:
		ctx.update(instance.file.read())

	hash = ctx.hexdigest()

	return os.path.join(file_dir, hash[0], hash, filename)


class Map(models.Model):
	"""
	A map listing
	"""
	QUAKE1 = 'q1'
	QUAKE2 = 'q2'
	QUAKE3 = 'q3'
	GAME_CHOICES = [
		(QUAKE1, 'Quake 1'),
		(QUAKE2, 'Quake 2'),
		(QUAKE3, 'Quake 3'),
	]

	name = models.CharField(max_length=64)
	created = models.DateField(default=datetime.now)
	modified = models.DateField(blank=True, null=True)
	rating = models.FloatField(blank=True, null=True) # a value from 1.0 to 5.0
	game = models.CharField(max_length=2, choices=GAME_CHOICES, default=QUAKE1)
	homepage = models.URLField(blank=True, null=True)
	published = models.BooleanField(default=False) # should the map be visible

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		# return reverse('detail', args=[str(self.id)])
		return '/maps/%i/' % self.id


def mappackage_upload_to(instance, filename):
	"""
	Create the upload path to the new file, e.g., `maps/by-sha256/0/001.../filename.ext`
	"""
	return os.path.join('maps/by-sha256', instance.hash[0], instance.hash, filename)


class MapPackage(models.Model):
	file = models.FileField(upload_to=mappackage_upload_to, unique=True)
	file_name = models.CharField(max_length=128, blank=True, null=True)
	file_hash = models.CharField(max_length=64, blank=True, null=True, unique=True) # a sha256 hex hash of this file
	created = models.DateField(default=datetime.now)
	map = models.ForeignKey(Map, related_name='packages', on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return self.file.name


@receiver(post_delete, sender=MapPackage)
def mappackage_delete(sender, instance, **kwargs):
	"""
	Remove the file from disk when the MapPackage instance is deleted
	"""
	instance.file.delete(False) # False so FileField doesn't save the model


@receiver(pre_save, sender=MapPackage)
def mappackage_pre_save(sender, instance, *args, **kwargs):
	"""
	Before we save the instance, save the SHA256 hash of
	the file and its original filename for later
	"""
	ctx = hashlib.sha256()

	if instance.file.multiple_chunks():
		for data in instance.file.chunks(ctx.block_size):
			ctx.update(data)
	else:
		ctx.update(instance.file.read())

	instance.name = os.path.basename(instance.file.name)
	instance.hash = ctx.hexdigest()


class Tag(models.Model):
	name = models.CharField(max_length=32, unique=True)
	maps = models.ManyToManyField(Map, related_name='tags')

	def __str__(self):
		return self.name

	class Meta:
		ordering = ('name',)


class Author(models.Model):
	name = models.CharField(max_length=32, unique=True)
	full_name = models.CharField(max_length=64, blank=True, null=True)
	maps = models.ManyToManyField(Map, related_name='authors')
	homepage = models.URLField(blank=True, null=True)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ('name',)


class Review(models.Model):
	map = models.ForeignKey(Map, related_name='reviews', on_delete=models.CASCADE)
	user = models.CharField(max_length=32)
	rating = models.IntegerField(blank=True, null=True) # a value from 1 to 5


class MapUrls(models.Model):
	# a list of external URLs for a map
	name = models.CharField(max_length=32)
	url = models.URLField()
	map = models.ForeignKey(Map, related_name='urls', on_delete=models.CASCADE)

	def __str__(self):
		return self.name


class MapFile(models.Model):
	name = models.CharField(max_length=128)
	size = models.IntegerField()
	timestamp = models.DateTimeField(blank=True, null=True)
	map = models.ForeignKey(Map, related_name='files', on_delete=models.CASCADE)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ('name',)


class Screenshot(models.Model):
	image = models.ImageField(upload_to=map_screenshot_path)
	thumbnail = ImageSpecField(source='image',
							   processors=[ResizeToFit(640, 360)],
							   format='JPEG',
							   options={'quality': 60})
	map = models.ForeignKey(Map, related_name='screenshots', on_delete=models.CASCADE)

	@classmethod
	def get_image_basedir(cls):
		return 'maps/screenshots'

	def __str__(self):
		return self.image.name


@receiver(post_delete, sender=Screenshot)
def map_screenshot_delete(sender, instance, **kwargs):
	# Pass false so FileField doesn't save the model.
	instance.image.delete(False)


class Demo(models.Model):
	SKILL_CHOICES = [
		(0, 'Easy'),
		(1, 'Normal'),
		(2, 'Hard'),
		(3, 'Nightmware'),
	]
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	file = models.FileField()
	skill = models.IntegerField(choices=SKILL_CHOICES, default=1)
	length = models.IntegerField()
	protocol = models.IntegerField(blank=True, null=True)
	created = models.DateTimeField()
	description = models.CharField(max_length=256, blank=True, null=True)
	package = models.ForeignKey(MapPackage, on_delete=models.CASCADE)
	video_url = models.URLField(blank=True, null=True)
