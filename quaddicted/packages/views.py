from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, QueryDict, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.db.models import Q, Count, F, FloatField
from django.db.models.functions import Round
from django.utils.http import urlencode
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_http_methods, require_GET, require_safe
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import DetailView, UpdateView, ListView
from django.core.paginator import EmptyPage

from django.forms import inlineformset_factory

from extra_views import ModelFormSetView, NamedFormsetsMixin
from extra_views import CreateWithInlinesView, UpdateWithInlinesView


import json

from .models import Package, Rating, Screenshot
from .forms import RatingForm, PackageEditForm, PackageCreateForm, ScreenshotInline
from django_comments.models import Comment



# https://docs.djangoproject.com/en/3.0/ref/models/database-functions/#round
# Register ROUND as a transform
FloatField.register_lookup(Round)



class PackageListView(ListView):
	model = Package
	context_object_name = 'package_list'
	ordering = '-created'
	template_name = 'packages/package_list.html'
	ordering = '-created'
	paginate_by = 21
	queryset = Package.objects.filter(published=True)

	sort_fields = {
		'name': 'asc',
		'created': 'desc',
		'rating': 'desc',
	}

	def get_ordering(self):
		sort = self.request.GET.get('sort')
		if sort:
			sort_field = sort[1:] if sort.startswith('-') else sort

			if sort_field in self.sort_fields.keys():
				# Set the view ordering property
				return sort
		else:
			# Default to sorting by created date in descending order
			return '-created'

	def get(self, request, *args, **kwargs):
		#
		# Sorting
		# update the sorting field dict for table headers
		#
		sort = request.GET.get('sort')
		if sort:
			sort_field = sort[1:] if sort.startswith('-') else sort

			if sort_field in self.sort_fields.keys():
				# invert this sort field
				self.sort_fields[sort_field] = 'asc' if sort.startswith('-') else 'desc'
		else:
			# Default is to sort by created in desc order
			# so the link should be asc order
			self.sort_fields['created'] = 'asc'

		for field, descending in self.sort_fields.items():
			# toggle the sort direction of the requested field
			self.sort_fields[field] = '-' + field if descending == 'desc' else field

		self.object_list = self.get_queryset()

		#
		# Author Filtering
		#
		authors = request.GET.getlist('author', [])
		for author in authors:
			self.object_list = self.object_list.filter(authors__slug=author).distinct()

		#
		# Tag Filtering
		#
		try:
			tags = request.GET.getlist('tag')
		except KeyError:
			tags = []

		for tag in tags:
			self.object_list = self.object_list.filter(tags__slug=tag).distinct()

		#
		# Rating Score Filtering
		# e.g., ?rating=3
		#
		rating = request.GET.get('rating', None)
		if rating is not None:
			try:
				self.object_list = self.object_list.filter(rating__gte=int(rating))
			except ValueError:
				pass

		#
		# Searching
		#
		search = request.GET.get('search', None)
		if search is not None:
			self.object_list = self.object_list.filter(
				Q(name__icontains=search) |
				Q(tags__name__icontains=search) |
				Q(authors__name__icontains=search)
			).distinct()

		# get_context_data will add as package_list
		self.object_list = self.object_list.order_by(self.get_ordering())

		context = self.get_context_data(
			# package list table sort links
			sort_fields = self.sort_fields,

			# set the main navbar section active
			active_section = 'packages',

			# we need the querystring dictionary to create filtering links
			querydict = request.GET,

			# list of authors being filtered on
			filtered_authors = authors,

			# list of tags filtered for
			filtered_tags = tags,

			# search term being searched for
			filtered_term = search,
		)

		return self.render_to_response(context)



class PackageCardView(PackageListView):
	template_name = 'packages/package_cards.html'



def detail(request, package_hash):
	package = get_object_or_404(Package, file_hash=package_hash)

	#
	# Ratings
	#
	# Get the tallies of each rating value (1 to 5)
	rating_qset = package.ratings.all().values('score').annotate(Count('score'))
	rating_dict = {r['score']: r['score__count'] for r in rating_qset}
	rating_list = [rating_dict.get(i, 0) for i in range(1, 6)]

	user_rating = None
	if request.user.id:
		try:
			user_rating = package.ratings.get(user=request.user.id).score
		except ObjectDoesNotExist:
			pass


	#
	# Comments
	#
	package_content_type = ContentType.objects.get_for_model(Package)

	# Can't figure out how to do this with the ORM
	tbl_rating = Rating._meta.db_table
	# comments = Comment.objects.raw('SELECT * FROM quaddicted_comments_quaddictedcommentmodel LEFT JOIN quaddicted_packages_rating ON quaddicted_comments_quaddictedcommentmodel.user_id=quaddicted_packages_rating.user_id AND quaddicted_packages_rating.package_id=CAST(object_pk AS INTEGER) WHERE content_type_id=%s AND CAST(object_pk AS INTEGER)=%s', [package_content_type.id, package.id,])
	comments = Comment.objects.raw('SELECT * FROM django_comments LEFT JOIN {tbl_rating} ON django_comments.user_id={tbl_rating}.user_id AND {tbl_rating}.package_id=CAST(object_pk AS INTEGER) WHERE content_type_id=%s AND CAST(object_pk AS INTEGER)=%s'.format(tbl_rating=tbl_rating), [package_content_type.id, package.id,])

	#
	# Rating Submission
	#
	# TODO: make this less ugly; maybe ModelForm?
	if request.method == 'POST':
		rating_form = RatingForm(request.POST)

		if rating_form.is_valid():
			score = rating_form.cleaned_data['score']

			rating_obj, created = Rating.objects.update_or_create(
				user=request.user,
				package=package,
				defaults={
					'username': request.user.get_username(),
					'score': score,
				}
			)

			rating_obj.save()
			return HttpResponseRedirect(package.get_absolute_url())
	else:
		rating_form = RatingForm()

	#
	# Screenshots
	#
	screenshots = Screenshot.objects.filter(package=package).order_by('pk')

	return render(request, 'packages/package_detail.html', {
		'package': package,
		'active_section': 'packages',
		'num_ratings': package.ratings.count(),
		'rating_list': rating_list,
		'user_rating': user_rating,
		'comments': comments,
		'rating_qset': rating_qset,
		'screenshots': screenshots,
	})



@require_safe
def package_form(request):
	"""
		Upload a new package
	"""
	return render(request, 'packages/package_form.html', {
		'form': PackageForm(),
	})



class PackageCreate(LoginRequiredMixin, NamedFormsetsMixin, CreateWithInlinesView):
	inlines = [ScreenshotInline,]
	inlines_names = ['screenshot_inline',]
	template_name = 'packages/package_form.html'
	model = Package
	form_class = PackageCreateForm

	def form_valid(self, form):
		form.instance.uploaded_by = self.request.user
		return super().form_valid(form)

	def get_context_data(self, *args, **kwargs):
		return super().get_context_data(*args, active_section='packages', **kwargs)



@login_required
@permission_required('quaddicted_packages.change_package')
def package_edit(request, package_hash):
	package = get_object_or_404(Package, file_hash=package_hash)
	ScreenshotFormSet = inlineformset_factory(Package, Screenshot, exclude=())

	if request.method == 'POST':
		package_form = PackageEditForm(request.POST, request.FILES, instance=package)
		screenshot_formset = ScreenshotFormSet(request.POST, request.FILES, instance=package)

		if package_form.is_valid():
			package_form.save()

		if screenshot_formset.is_valid():
			screenshot_formset.save()

		if "_continue" in request.POST:
			return HttpResponseRedirect(reverse('packages:edit', kwargs={'package_hash': package.file_hash}))
		else:
			return HttpResponseRedirect(package.get_absolute_url())
	else:
		package_form = PackageEditForm(instance=package)
		screenshot_formset = ScreenshotFormSet(instance=package)
		return render(request, 'packages/package_form.html', {
			'object': package,
			'form': package_form,
			'screenshot_inline': screenshot_formset,
		})



@login_required
@require_POST
def tag_form(request, package_hash):
	"""
		POST tag suggestions and changes here
	"""
	return HttpResponse('This is the tags view POST')



@login_required
@require_GET
def tag_form(request, package_hash):
	"""
		Return a form for suggesting new tags
	"""
	return HttpResponse('This is the tags view GET')



def rating_form(request, package_hash):
	pass



def comment_form(request, package_hash):
	pass



def demo_form(request, package_hash):
	pass
