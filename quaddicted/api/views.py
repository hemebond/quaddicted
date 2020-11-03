from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from quaddicted.packages.models import Package
from quaddicted.packages.views import package_list as package_list_html, package_list_cards, package_list_filter, package_detail as package_detail_html
from .serializers import PackageSerializer, CommentSerializer
from rest_framework.pagination import PageNumberPagination



class PackageListPaginator(PageNumberPagination):
	page_size = 21
	page_size_query_param = 'page_size'
	max_page_size = 99



class PackageCommentListPaginator(PageNumberPagination):
	page_size = 20
	page_size_query_param = 'page_size'
	max_page_size = 99



class CardRenderer(TemplateHTMLRenderer):
	"""
	A custom renderer just so we can accept the 'card' format querystring parameter
	"""
	format = 'card'



@api_view()
@renderer_classes([TemplateHTMLRenderer, CardRenderer, JSONRenderer, BrowsableAPIRenderer])
def package_list(request):
	format = request.accepted_renderer.format

	if format == 'html':
		return package_list_html(request)

	if format == 'card':
		return package_list_cards(request)

	sort = request.GET.get('sort', '-created')
	packages = Package.objects.filter(published=True)
	packages = package_list_filter(request, packages).distinct().order_by(sort)

	paginator = PackageListPaginator()
	page = paginator.paginate_queryset(packages, request)
	serializer = PackageSerializer(page, many=True, context={"request": request})

	return paginator.get_paginated_response(serializer.data)



@api_view(['GET', 'POST'])
@renderer_classes([TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer])
def package_detail(request, file_hash):
	format = request.accepted_renderer.format

	if format == 'html':
		return package_detail_html(request, package_hash=file_hash)

	package = Package.objects.get(file_hash=file_hash)
	serializer = PackageSerializer(package, context={"request": request})

	return Response(serializer.data)



@api_view()
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def package_comments(request, file_hash):
	package = get_object_or_404(Package, file_hash=file_hash)
	comments = package.comments.all()

	paginator = PackageCommentListPaginator()
	page = paginator.paginate_queryset(comments, request)
	serializer = CommentSerializer(page, many=True, context={"request": request})

	return paginator.get_paginated_response(serializer.data)
