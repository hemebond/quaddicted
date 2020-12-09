import os
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from taggit.utils import edit_string_for_tags

register = template.Library()


@register.simple_tag
def filter_on_tag(request, tag):
	d = request.GET.copy()
	d.setlist('tag', [tag])
	return d.urlencode()


@register.simple_tag
def filter_add_tag(request, tag):
	d = request.GET.copy()
	d.appendlist('tag', tag)
	try:
		d.pop('page')
	except KeyError:
		pass
	return d.urlencode()


@register.simple_tag
def filter_del_tag(request, tag):
	d = request.GET.copy()
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
def qs_update(request, **kwargs):
	querydict = request.GET.copy()

	for k, v in kwargs.items():
		if v is not None:
			querydict[k] = v
		else:
			querydict.pop(k, 0)

	return querydict.urlencode()


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
	return mark_safe(icon('star') * int(rating))


@register.simple_tag
def icon(icon):
	# return mark_safe('<svg class="icon" viewBox="0 0 10 10"><use href="' + settings.STATIC_URL + '/ext/fontawesome-free-5.12.0-web/sprites/solid.svg#' + icon + '"></use></svg>')
	# return mark_safe('<svg class="icon" viewBox="0 0 10 10"><use href="' + settings.STATIC_URL + '/fa/' + icon + '.svg"></use></svg>')
	return mark_safe('<svg class="icon" viewBox="0 0 1 1"><use href="' + settings.STATIC_URL + 'fontawesome.svg#' + icon + '"></use></svg>')


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


@register.filter
def strftags(value):
	"""
	Convert the "tags" value of a model
	into a string for use as form field value, e.g.:
	value="{{ f.value|edit_tags|default_if_none:'' }}"
	"""
	if value is not None and not isinstance(value, str):
		return edit_string_for_tags(value)
	return value


@register.simple_tag
def odir(obj):
	"""
	Returns the object properties and methods as a string to help debug
	"""
	return str(dir(obj))


@register.filter
def basename(value):
	return os.path.basename(value)



@register.simple_tag
def get(obj, key):
	return obj.get(key, None)



@register.simple_tag
def sort_th(request, sort_by, title):
	"""
	"sort_by" is the field name with "-" prefix for descending sort
	"title" is the text for the TH element
	"""
	current_sort = request.GET.get('sort', None)

	if current_sort is not None:
		if current_sort == sort_by:
			if sort_by[0] == "-":
				sort_by = sort_by[1:]
			else:
				sort_by = "-" + sort_by

	# if we're sorting by this field already, invert it


	return ""
