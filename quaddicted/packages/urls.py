from django.urls import path

from . import views

app_name = 'packages'
urlpatterns = [
	path('', views.package_list, name='list'),
	path('cards/', views.package_list_cards, name='cards'),
	path('new/', views.package_add, name='new'),
	path('<str:package_hash>/', views.package_detail, name='detail'),
	path('<str:package_hash>/edit/', views.package_edit, name='edit'),
	path('<str:package_hash>/tags/', views.tag_form, name='tags'),
	path('<str:package_hash>/ratings/', views.rating_form, name='ratings'),
	path('<str:package_hash>/comments/', views.comment_form, name='comments'),
]
