import os
import sys
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from taggit.utils import edit_string_for_tags
from django.utils.translation import gettext as _
from django.urls import reverse

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
def rating_stars(score):
	return mark_safe('<span class="rating-%s">%s</span>' % (int(score), icon('star') * int(score)))


@register.simple_tag
def icon(icon):
	# return mark_safe('<svg class="icon" viewBox="0 0 10 10"><use href="' + settings.STATIC_URL + '/ext/fontawesome-free-5.12.0-web/sprites/solid.svg#' + icon + '"></use></svg>')
	# return mark_safe('<svg class="icon" viewBox="0 0 10 10"><use href="' + settings.STATIC_URL + '/fa/' + icon + '.svg"></use></svg>')
	return mark_safe('<svg class="icon" viewBox="0 0 1 1"><use href="' + settings.STATIC_URL + 'fontawesome.svg#' + icon + '"></use></svg>')



@register.simple_tag
def rating_badge(score):
	return mark_safe('<span class="badge rating-bg-%s">%s</span>' % (int(score), int(score)))



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



@register.inclusion_tag("includes/nav_links.html", takes_context=True)
def nav_links(context):
	user = context.request.user
	resolver_match = context.request.resolver_match

	links = {
		"home": {
			"href": "/",
			"text": _("Home"),
			"active": resolver_match.url_name == 'home',
		},
		"news": {
			"href": "/news/",
			"text": _("News"),
			"active": resolver_match.url_name == 'news',
		},
		"packages": {
			"href": reverse("packages:list"),
			"text": _("Maps"),
			"active": resolver_match.route.startswith("packages/")
		},
		"forum": {
			"href": reverse("djangobb:index"),
			"text": _("Forum"),
			"active": resolver_match.route.startswith("forum/")
		},
		"help": {
			"href": "/help/",
			"text": _("Help"),
		},
		"login": {
			"href": reverse("auth_login"),
			"text": _("Login"),
			"active": resolver_match.url_name in ("auth_login", "auth_logout")
		},
	}

	# give logged-in users a logout link instead
	if user.is_authenticated:
		links['login'].update({
			"href": reverse("auth_logout"),
			"text": _("Logout"),
		})

	# return just the plain list of links
	return {"links": links.values()}



@register.inclusion_tag("includes/sort_th.html")
def sort_th(request, text, sort_by, icon_asc="sort-up", icon_desc="sort-down"):
	"""
	"sort_by" is the field name with "-" prefix for descending sort
	"title" is the text for the TH element

	if this is in the list but not the last, sort by default
	if this is the last-sorted field, then invert
	"""

	def _parse_sort(s):
		"""
		Parses a sort string and returns the name and whether it's asc (True) or desc (False)
		"""
		if s[0] == '-':
			return (s[1:], False)
		return (s, True)

	# what the TH link will sort
	sort_by_name, sort_by_asc = _parse_sort(sort_by)

	# the current list of sorted fields
	current_list = request.GET.getlist('sort', [])

	# get the current field if it's been sorted on
	sorted_field = None
	for field in current_list:
		if _parse_sort(field)[0] == sort_by_name:
			current_field_name, current_field_asc = _parse_sort(field)

	# remove this field form the current sort list
	new_sort_list = [
		field
		for field
		in current_list
		if _parse_sort(field)[0] != sort_by_name
	]

	# the last field to be sorted
	is_last_sort = False
	if current_list:
		last_sort_name, last_sort_asc = _parse_sort(current_list[-1])

		if sort_by_name != last_sort_name:
			# if this field was _not_ the last to be sorted
			# put it onto the end of the list
			new_sort_list.append(sort_by)
		else:
			# this field was the last/most recent to be sorted
			# so add it to the end but invert its direction
			if last_sort_asc:
				new_sort_list.append("-%s" % sort_by_name)
				sort_by_asc = True
			else:
				new_sort_list.append(sort_by_name)
				sort_by_asc = False

			is_last_sort = True
	else:
		new_sort_list = [sort_by,]

	# make new sort list into querystring
	querydict = request.GET.copy()
	querydict.setlist('sort', new_sort_list)
	querystring = querydict.urlencode()

	ret = {
		"text": text,
		"querystring": querystring,
		"sort_icon": icon_asc if sort_by_asc else icon_desc,
		"sorted": is_last_sort,
	}
	return ret



"""
Markdown2 filter, requires the python-markdown2 library from
http://code.google.com/p/python-markdown2

This code is based on django's markup contrib.
"""
if sys.version_info.major == 2:
    from django.utils.encoding import force_unicode
else:
    force_unicode = lambda text: text

@register.filter
def markdown(value, arg=''):
    """
    Runs Markdown over a given value, optionally using various
    extensions python-markdown supports.

    Syntax::

        {{ value|markdown2:"extension1_name,extension2_name..." }}

    To enable safe mode, which strips raw HTML and only returns HTML
    generated by actual Markdown syntax, pass "safe" as the first
    extension in the list.

    If the version of Markdown in use does not support extensions,
    they will be silently ignored.
    """
    try:
        import markdown2
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError("Error in {% markdown %} filter: The python-markdown2 library isn't installed.")
        return force_unicode(value)
    else:
        def parse_extra(extra):
            if ':' not in extra:
                return (extra, {})
            name, values = extra.split(':', 1)
            values = dict((str(val.strip()), True) for val in values.split('|'))
            return (name.strip(), values)

        extras = (e.strip() for e in arg.split(','))
        extras = dict(parse_extra(e) for e in extras if e)

        if 'safe' in extras:
            del extras['safe']
            safe_mode = True
        else:
            safe_mode = False

        return mark_safe(markdown2.markdown(force_unicode(value), extras=extras, safe_mode=safe_mode))
markdown.is_safe = True
