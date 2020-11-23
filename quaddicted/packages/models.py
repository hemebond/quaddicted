from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg, Sum, Count, Q
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from django.utils.translation import ugettext_lazy as _

from pathlib import Path

import os
import hashlib

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from taggit.managers import TaggableManager
from django_comments.models import Comment

# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver



def calculate_file_hash(file_object):
	"""
	Calculate the sha256 hash of an uploaded file
	"""
	ctx = hashlib.sha256()

	if file_object.multiple_chunks():
		for data in file_object.chunks(ctx.block_size):
			ctx.update(data)
	else:
		ctx.update(file_object.read())

	return ctx.hexdigest()



def package_upload_to(instance, filename):
	"""
	Create the upload path to the new file, e.g., `maps/by-sha256/0/001.../filename.ext`
	"""
	return os.path.join('packages', instance.file_hash[0], instance.file_hash, filename)



def validate_package_file(value):
	# In-memory files (files being uploaded) have a content_type attribute
	# whereas files already uploaded do not
	try:
		if value.file.content_type != 'application/zip':
			raise ValidationError('File must be a zip')
	except AttributeError:
		pass





class Package(models.Model):
	class PackageGame(models.TextChoices):
		QUAKE1 = 'q1', _('Quake 1')
		QUAKE2 = 'q2', _('Quake 2')
		QUAKE3 = 'q3', _('Quake 3')

	class PackageType(models.IntegerChoices):
		BSP = 1, _("Single BSP File(s)")
		PARTIAL_CONVERSION = 2, _("Partial conversion")
		TOTAL_CONVERSION = 3, _("Total conversion")
		SPEEDMAPPING = 4, _("Speedmapping")
		MISC_FILES = 5, _("Misc. Files")
		UNDEFINED = 6, _("undefined, please tell Spirit")

	# package file properties
	file = models.FileField(upload_to=package_upload_to, max_length=256, validators=[validate_package_file,])
	file_name = models.CharField(max_length=128, blank=True, editable=False)  # the filename of the file, e.g., something.zip
	file_hash = models.CharField(max_length=64, blank=True, editable=False, unique=True)  # sha256 hash of the .zip file and also the primary key
	file_size = models.BigIntegerField(blank=True, null=True, editable=False)

	# package properties
	name = models.CharField(max_length=128)  # the name or title of the package
	created = models.DateTimeField(auto_now_add=True)  # timestamp of the newest file in the package
	rating = models.FloatField(blank=True, null=True, editable=False)  # average of all the user ratings, a value from 1.0 to 5.0
	game = models.CharField(max_length=2, choices=PackageGame.choices, default=PackageGame.QUAKE1)  # which game is this package for
	description = models.TextField(blank=True)
	type = models.IntegerField(choices=PackageType.choices, default=PackageType.UNDEFINED)

	tags = TaggableManager(blank=True)
	authors = models.ManyToManyField('PackageAuthor',
	                                 related_name='packages',
	                                 help_text="A comma-separated list of authors.")
	comments = GenericRelation(Comment,
	                           content_type_field="content_type",
	                           object_id_field="object_pk")

	# management info
	published = models.BooleanField(default=False)  # package not public until published
	uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	uploaded_on = models.DateTimeField(auto_now_add=True, editable=False)  # when was this package uploaded?

	# execution properties
	base_dir = models.CharField(max_length=256,
	                            blank=True,
	                            null=True,
	                            help_text="directory where this package should be extracted to")
	command_line = models.CharField(max_length=256,
	                                blank=True,
	                                null=True,
	                                help_text="command-line arguments for running the package")
	dependencies = models.ManyToManyField('self', symmetrical=False)
	start_map = models.CharField(max_length=64,
	                             blank=True,
	                             null=True,
	                             help_text="which map should be loaded")


	def clean(self, *args, **kwargs):
		if not self.file_hash:
			update_file_details(self)
		super().clean(*args, **kwargs)


	def save(self, *args, **kwargs):
		if not self.file_hash:
			update_file_details(self)
		super().save(*args, **kwargs)


	def __str__(self):
		return self.name


	class Meta:
		ordering = ('name',)


	def get_absolute_url(self):
		return reverse('packages:detail', args=[str(self.file_hash)])



def update_file_details(package_instance):
	"""
	Update the package instance with extra detail about the uploaded file
	"""
	f = package_instance.file

	package_instance.file_hash = calculate_file_hash(f)
	package_instance.file_name = Path(f.name).name
	package_instance.file_size = f.size

	try:
		existing_package = Package.objects.get(file_hash=package_instance.file_hash)
	except Package.DoesNotExist:
		pass
	else:
		err_msg = format_html(_("File <code>{}</code> has been uploaded to package <a href=\"{}\">{}</a>"),
			str(f),
			mark_safe(existing_package.get_absolute_url()),
			str(existing_package)
		)
		raise ValidationError(err_msg)



@receiver(post_delete, sender=Package)
def package_delete(sender, instance, **kwargs):
	"""
	Remove the file from disk when the Package instance is deleted
	"""
	instance.file.delete(False)  # False so FileField doesn't save the model



class PackageAuthor(models.Model):
	name = models.CharField(verbose_name=_("name"), unique=True, max_length=100)
	slug = models.SlugField(verbose_name=_("slug"), unique=True, max_length=100)

	class Meta:
		verbose_name = _("Package Author")
		verbose_name_plural = _("Package Authors")

	def __str__(self):
		return self.name



class PackageRating(models.Model):
	"""
	A package rating. Scale is 1 to 5.
	"""
	# the User account who created the rating
	user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
	# used to store the username when user is deleted or never existed
	username = models.CharField(max_length=32, blank=True, null=True)
	package = models.ForeignKey(Package, related_name='ratings', on_delete=models.CASCADE)
	# a value from 1 to 5
	score = models.PositiveSmallIntegerField(
		validators=[
			validators.MinValueValidator(1),
			validators.MaxValueValidator(5),
		]
	)
	created = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = [
			['user', 'package'],
			['username', 'package'],
		]



@receiver(post_save, sender=PackageRating, dispatch_uid="new_rating")
@receiver(post_delete, sender=PackageRating, dispatch_uid="del_rating")
def update_package_rating(sender, instance, **kwargs):
	# Update the rating for a package
	# when it gains or loses a rating
	bayesian = calculate_bayesian_average(package_pk=instance.package_id)
	instance.package.rating = bayesian
	instance.package.save()



def calculate_bayesian_average(package_pk):
	"""
	https://github.com/SpiritQuaddicted/Quaddicted-reviews/blob/master/index.php#L187

	Taken from the original Quaddicted code. Calculates a
	modified version of the bayesian average of its ratings.
	"""
	packages = Package.objects.annotate(sum_ratings=Coalesce(Sum('ratings__score'), 0)).annotate(num_ratings=Count('ratings'))
	package = packages.get(pk=package_pk)

	sum_ratings = package.ratings.aggregate(sum=Sum('score'))['sum']

	if sum_ratings and sum_ratings > 0:
		avg_num_ratings = packages.filter(~Q(ratings=None)).aggregate(avg=Avg('num_ratings'))['avg']
		sum_sum_ratings = PackageRating.objects.aggregate(sum=Sum('score'))['sum']
		sum_num_ratings = PackageRating.objects.count()

		bayesian = (
			avg_num_ratings * (
				sum_sum_ratings / sum_num_ratings
			) + package.num_ratings * (
				package.sum_ratings / package.num_ratings
			)
		) / (avg_num_ratings + package.num_ratings)

		return bayesian
	else:
		return None


class PackageUrl(models.Model):
	"""
	External URLs for a package
	"""
	name = models.CharField(max_length=32)
	url = models.URLField()
	package = models.ForeignKey(Package, related_name='urls', on_delete=models.CASCADE)

	def __str__(self):
		return self.name



class PackageFile(models.Model):
	"""
	Files contained within the package
	"""
	name = models.CharField(max_length=256) # full path of file inside archive
	last_modified = models.DateTimeField(auto_now_add=True) # when file was last modified
	size = models.BigIntegerField(blank=True, null=True, editable=False)
	package = models.ForeignKey(Package, related_name='files', on_delete=models.CASCADE)

	def __str__(self):
		return self.name



class PackageMap(models.Model):
	name = models.CharField(max_length=64, blank=True, null=True, help_text="Name of the map")
	file_name = models.CharField(max_length=64, help_text="File name stem (no extension) of the map")
	package = models.ForeignKey(Package, related_name="maps", on_delete=models.CASCADE)

	def __str__(self):
		return self.name



def screenshot_upload_to(instance, filename):
	return os.path.join('packages', instance.package.file_hash[0], instance.package.file_hash, filename)



class PackageScreenshot(models.Model):
	"""
	Packages can have zero or more screenshots associated with it.
	Thumbnails are automatically created.
	"""
	image = models.ImageField(upload_to=screenshot_upload_to,
	                          max_length=256,
	                          help_text="A 16x9 resolution image at least 1024x576")
	thumbnail = ImageSpecField(source='image',
							   processors=[ResizeToFit(384, 216)],
							   format='JPEG',
							   options={'quality': 60})
	package = models.ForeignKey(Package, related_name='screenshots', on_delete=models.CASCADE)

	def __str__(self):
		return self.image.name



@receiver(post_delete, sender=PackageScreenshot)
def screenshot_delete(sender, instance, **kwargs):
	# Pass false so FileField doesn't save the model.
	instance.image.delete(False)
