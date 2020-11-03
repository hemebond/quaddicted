"""quaddicted URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

from quaddicted.views import LogoutView, HomePageView, HomePageNewView
from quaddicted.packages.views import PackageCreate
from quaddicted.api.views import package_list, package_detail, package_comments



urlpatterns = [
	path('accounts/logout/', LogoutView.as_view(), name='auth_logout'),
	path('admin/', admin.site.urls),
	path('forum/', include('djangobb_forum.urls')),
	path('packages/new/', PackageCreate.as_view()),
	path('packages/', include('quaddicted.api.urls')),
	path('packages/', include('quaddicted.packages.urls')),
	path('comments/', include('django_comments.urls')),
	path('accounts/', include('registration.backends.default.urls')),
	path('', HomePageView.as_view(), name='homepage'),
	path('home/', HomePageNewView.as_view(), name='homepagenew'),
]


if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
