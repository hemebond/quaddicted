from django.urls import path

from . import views

app_name = 'maps'
urlpatterns = [
	path('', views.table, name='index'),
	path('cards/', views.cards, name='cards'),
	path('<int:map_id>/', views.detail, name='detail'),
	path('<int:map_id>/comment/', views.comment, name='comment'),
	path('<int:map_id>/steam/', views.steam, name='steam'),
]
