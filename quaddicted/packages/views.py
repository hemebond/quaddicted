from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, Count, FloatField
from django.db.models.functions import Round
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_POST, require_GET, require_safe

from .models import Package, PackageRating, PackageScreenshot, PackageUrl, PackageAuthor
from .forms import RatingForm, PackageEditForm, PackageCreateForm
from django_comments.models import Comment



# https://docs.djangoproject.com/en/3.0/ref/models/database-functions/#round
# Register ROUND as a transform
FloatField.register_lookup(Round)



def package_list_filter(request, queryset):
	"""
	Filters a queryset of Package objects based on the request
	"""

	#
	# Author Filtering
	#
	authors = request.GET.getlist('author', [])
	for author in authors:
		queryset = queryset.filter(created_by__slug=author)

	#
	# Tag Filtering
	# e.g., ?tag=runic&tag=halloween
	#
	tags = request.GET.getlist('tag', [])
	for tag in tags:
		queryset = queryset.filter(tags__slug=tag)

	#
	# Rating Score Filtering
	# e.g., ?rating=3
	#
	rating = request.GET.get('rating', None)
	if rating is not None:
		try:
			queryset = queryset.filter(rating__gte=int(rating))
		except ValueError:
			# Raised if the rating isn't actually an integer
			pass

	#
	# Text Search
	#
	search = request.GET.get('search', None)
	if search is not None:
		queryset = queryset.filter(
			Q(name__icontains=search) |
			Q(tags__name__icontains=search) |
			Q(created_by__name__icontains=search)
		)

	return queryset



def package_list_context(request):
	#
	# Filtering
	#
	packages = Package.objects.filter(published=True)
	# packages = package_list_filter(request, packages).distinct().order_by(sort)
	packages = package_list_filter(request, packages).distinct()

	#
	# Sorting order form request or use defaults
	#
	sort = request.GET.getlist('sort', [
		"name",
		"-rating",
		"-uploaded_at",
	])

	#
	# Update the sorting field dict for table headers
	#
	packages = packages.order_by(*sort[::-1])

	#
	# Pagination
	#
	paginator = Paginator(
		packages,
		request.GET.get('page_size', 21),
	)
	page_number = request.GET.get('page')
	page = paginator.get_page(page_number)

	context = {
		# list of authors being filtered on
		'filtered_authors': request.GET.getlist('author', []),

		# list of tags filtered for
		'filtered_tags': request.GET.getlist('tag', []),

		# search term being searched for
		'filtered_term': request.GET.get('search', ''),

		'page': page,
	}
	return context



def package_list(request):
	context = package_list_context(request)

	return render(request,
	              'packages/package_list.html',
	              context)



def package_list_cards(request):
	context = package_list_context(request)
	context['package_list_type'] = "cards"

	return render(request,
	              'packages/package_cards.html',
	              context)



def package_detail(request, package_hash):
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
	tbl_rating = PackageRating._meta.db_table
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

			rating_obj, created = PackageRating.objects.update_or_create(
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
	screenshots = PackageScreenshot.objects.filter(package=package).order_by('pk')

	return render(request, 'packages/package_detail.html', {
		'package': package,
		'active_section': 'packages',
		'num_ratings': package.ratings.count(),
		'rating_list': rating_list,
		'user_rating': user_rating,
		'comments': comments,
		'rating_qset': rating_qset,
		'screenshots': screenshots,
		'can_edit': request.user.has_perm("quaddicted_packages.change_package") or request.user == package.uploaded_by,
	})



@require_safe
def package_form(request):
	"""
		Upload a new package
	"""
	return render(request, 'packages/package_form.html', {
		'form': PackageForm(),
	})



@login_required
def package_add(request):
	ScreenshotFormSet = inlineformset_factory(Package, PackageScreenshot, exclude=())
	PackageUrlFormSet = inlineformset_factory(Package, PackageUrl, exclude=())

	if request.method == 'POST':
		# print(request.POST)
		package_form = PackageCreateForm(request.POST, request.FILES)
		screenshot_formset = ScreenshotFormSet(request.POST, request.FILES)
		packageurl_formset = PackageUrlFormSet(request.POST, request.FILES)

		if package_form.is_valid() and screenshot_formset.is_valid() and packageurl_formset.is_valid():
			# Remove the created_by field before saving the new package instance
			author_names = package_form.cleaned_data.pop('created_by')

			# Save new package instance so we can attach screenshots and URLs
			new_package = package_form.save(commit=False)
			new_package.uploaded_by = request.user
			new_package.save()

			# save the tags
			package_form.save_m2m()

			#
			# Create Screenshots
			#
			screenshot_formset.instance = new_package
			screenshot_formset.save()

			#
			# Create URLs
			#
			packageurl_formset.instance = new_package
			packageurl_formset.save()

			#
			# Create Authors
			#
			author_set = set()

			# Take the comma-separated list of names and
			# create or fetch the PackageAuthor objects for them
			for author_name in author_names:
				author_slug = slugify(author_name, allow_unicode=True)
				author_obj, created = PackageAuthor.objects.get_or_create(name=author_name, slug=author_slug)
				author_set.add(author_obj)

			new_package.created_by.set(author_set)

			return HttpResponseRedirect(new_package.get_absolute_url())
		else:
			screenshot_formset = ScreenshotFormSet(request.POST, request.FILES)
			packageurl_formset = PackageUrlFormSet(request.POST, request.FILES)
	else:
		package_form = PackageCreateForm()
		screenshot_formset = ScreenshotFormSet()
		packageurl_formset = PackageUrlFormSet()

	return render(request, 'packages/package_form.html', {
		'form': package_form,
		'screenshot_inline': screenshot_formset,
		'packageurl_inline': packageurl_formset,
	})



@login_required
def package_edit(request, package_hash):
	package = get_object_or_404(Package, file_hash=package_hash)
	ScreenshotFormSet = inlineformset_factory(Package, PackageScreenshot, exclude=())
	PackageUrlFormSet = inlineformset_factory(Package, PackageUrl, exclude=(), extra=2)

	if request.method == 'POST':
		package_form = PackageEditForm(request.POST, request.FILES, instance=package)
		screenshot_formset = ScreenshotFormSet(request.POST, request.FILES, instance=package)
		packageurl_formset = PackageUrlFormSet(request.POST, request.FILES, instance=package)

		if package_form.is_valid() and screenshot_formset.is_valid() and packageurl_formset.is_valid():
			author_names = package_form.cleaned_data.pop('created_by')
			pkg = package_form.save()
			screenshot_formset.save()
			packageurl_formset.save()

			# print(author_names)
			author_set = set()

			# Take the comma-separated list of names and
			# create or fetch the PackageAuthor objects for them
			for author_name in author_names:
				author_slug = slugify(author_name, allow_unicode=True)
				try:
					author_obj, created = PackageAuthor.objects.get_or_create(name=author_name, slug=author_slug)
				except IntegrityError:
					author_obj = PackageAuthor.objects.get(slug=author_slug)
				author_set.add(author_obj)

			pkg.created_by.set(author_set)

			if "_continue" in request.POST:
				return HttpResponseRedirect(
					reverse('packages:edit', kwargs={'package_hash': package.file_hash})
				)
			else:
				return HttpResponseRedirect(package.get_absolute_url())
	else:
		package_form = PackageEditForm(instance=package)
		screenshot_formset = ScreenshotFormSet(instance=package)
		packageurl_formset = PackageUrlFormSet(instance=package)

	return render(request, 'packages/package_form.html', {
		'object': package,
		'form': package_form,
		'screenshot_inline': screenshot_formset,
		'packageurl_inline': packageurl_formset,
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
