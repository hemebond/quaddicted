from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, QueryDict
from django.template import loader
from django.db.models import Q
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

import json

from .models import Map
from .forms import CommentForm


def index(request, template):
	qd = request.GET.copy() # Clone the QueryDict so it's mutable
	map_list = Map.objects.all()

	authors = qd.getlist('author', [])
	if authors:
		map_list = map_list.filter(authors__in=authors)

	try:
		tags = qd.pop('tag')
	except KeyError:
		tags = []

	# for tag in tags:
		# try:
		# 	# map_list = map_list.filter(tags=int(tag))
		# except:
		# 	pass
	for tag in tags:
		try:
			map_list = map_list.filter(taggits__slug=tag).distinct()
		except:
			pass

	search_term = qd.get('search', None)
	if search_term:
		map_list = map_list.filter(
			Q(name__icontains=search_term) |
			Q(tags__name__icontains=search_term) |
			Q(authors__name__icontains=search_term))

	map_list = map_list.distinct()

	try:
		sort = qd.pop('sort')[0]
		map_list = map_list.order_by(sort)
	except KeyError:
		sort = '-created'
		map_list = map_list.order_by('-created')

	sort_defaults = [
		'name',
		'-created',
		'-rating',
	]

	if sort:
		def flip_order(field):
			if field == sort:
				if field.startswith('-'):
					return field[1:]
				else:
					return '-' + field
			else:
				return field

		sort_fields = list(map(flip_order, sort_defaults))
	else:
		sort_fields = sort_defaults

	# The query string without tags or sort
	qs = qd.urlencode()

	# base querystring for tag filtering
	qs_wo_tags = '&'.join([qs, urlencode({'sort': sort}, True)]) if sort else ''

	# base querystring for table sorting
	qs_wo_sort = '&'.join([qs, urlencode({'tag': tags}, True)]) if tags else ''

	context = {
		'map_list': map_list,
		'tag_list': tags, # list of tags filtered for
		'search_term': search_term,

		'sort_fields': sort_fields,

		# query strings for hyperlinks
		'qs': request.GET.urlencode(), # search_term, sort, tags
		'qs_wo_tags': qs_wo_tags,
		'qs_wo_sort': qs_wo_sort,
	}
	return render(request, template, context)


def table(request):
	return index(request, 'maps/table.html')


def cards(request):
	return index(request, 'maps/cards.html')


def detail(request, map_id):
	map = get_object_or_404(Map, pk=map_id)

	# if request.method == 'POST':
	# 	form = CommentForm(request.POST)

	# 	if form.is_valid():
	# 		form.save()
	# 		return redirect(map)
	# 	else:
	# 		print('form not vlaid')
	# else:
	# 	form = CommentForm()

	return render(request, 'maps/detail.html', {'map': map})


def steam(request, map_id):
	map = get_object_or_404(Map, pk=map_id)
	return render(request, 'maps/steam.html', {'map': map})
