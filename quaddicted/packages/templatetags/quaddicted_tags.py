import os
from django import template
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from taggit.utils import edit_string_for_tags

register = template.Library()


@register.simple_tag
def filter_on_tag(querydict, tag):
	d = querydict.copy()
	d.setlist('tag', [tag])
	return d.urlencode()


@register.simple_tag
def filter_add_tag(querydict, tag):
	d = querydict.copy()
	d.appendlist('tag', tag)
	try:
		d.pop('page')
	except KeyError:
		pass
	return d.urlencode()


@register.simple_tag
def filter_del_tag(querydict, tag):
	d = querydict.copy()
	tags = d.pop('tag')

	try:
		tags.remove(tag)
	except ValueError:
		# the tag isn't being filtered on
		pass

	if tags:
		d.setlist('tag', tags)

	return d.urlencode()


@register.simple_tag
def filter_by_author(querydict, author_slug):
	d = querydict.copy()
	d.setlist('author', [author_slug])
	return d.urlencode()


@register.simple_tag
def sort_by(querydict, sort_value):
	d = querydict.copy()
	d.setlist('sort', [sort_value])
	return d.urlencode()


@register.simple_tag
def rating_percentage(rating):
	return rating / 5


@register.simple_tag
def rating_for_user(package, user):
	return package.ratings.get(user=user).rating


@register.simple_tag
def icon_rating_for_user(package, user):
	return package.ratings.get(user=user).rating


@register.simple_tag
def rating_stars(rating):
	return mark_safe(' <i class="fas fa-star"></i>' * int(rating))


@register.filter
def edit_tags(value):
	"""
	Convert the "tags" value of a model
	into a string for use as form field value, e.g.:
	value="{{ f.value|edit_tags|default_if_none:'' }}"
	"""
	if value is not None and not isinstance(value, str):
		return edit_string_for_tags(value)
	return value


@register.simple_tag
def qs_set(querydict, keyname, value):
	d = querydict.copy()
	d.setlist(keyname, [value,])
	return d.urlencode()


@register.simple_tag
def odir(obj):
	"""
	Returns the object properties and methods as a string to help debug
	"""
	return str(dir(obj))


@register.filter
def basename(value):
	return os.path.basename(value)
