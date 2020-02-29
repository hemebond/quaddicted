from django.urls import path

from .views import PackageListView, PackageDetailView

urlpatterns = [
	path('packages/', PackageListView.as_view()),
	path('packages/<str:file_hash>/', PackageDetailView.as_view()),
]
