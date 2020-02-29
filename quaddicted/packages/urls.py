from django.urls import path

from . import views

app_name = 'packages'
urlpatterns = [
	path('', views.PackageListView.as_view(), name='list'),
	path('cards/', views.PackageCardView.as_view(), name='cards'),
	path('new/', views.PackageCreate.as_view(), name='new'),
	path('<str:package_hash>/', views.detail, name='detail'),
	path('<str:package_hash>/edit/', views.PackageEdit.as_view(), name='edit'),
	path('<str:package_hash>/tags/', views.tag_form, name='tags'),
	path('<str:package_hash>/ratings/', views.rating_form, name='ratings'),
	path('<str:package_hash>/comments/', views.comment_form, name='comments'),
	# path('<str:package_hash>/screenshots/add/', views.screenshot_form, name='screenshots'),
]
