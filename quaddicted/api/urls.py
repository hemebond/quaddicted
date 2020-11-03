from django.urls import path

from .views import package_list, package_detail, package_comments

app_name = 'api'
urlpatterns = [
	path('', package_list),
	path('<str:file_hash>/', package_detail),
	path('<str:file_hash>/comments/', package_comments),
]
