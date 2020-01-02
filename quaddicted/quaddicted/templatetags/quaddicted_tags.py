from django import template
from django.utils.http import urlencode

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
