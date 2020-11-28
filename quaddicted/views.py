from django.core.paginator import Paginator
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.generic.base import TemplateView
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect

from django.contrib.auth.views import LogoutView as AuthLogoutView

from quaddicted.packages.models import Package
from djangobb_forum.models import Topic



class LogoutView(AuthLogoutView):
	"""
	Log out the user and display the 'You are logged out' message.
	"""
	next_page = None
	redirect_field_name = REDIRECT_FIELD_NAME
	template_name = 'registration/logout.html'
	extra_context = None


	def dispatch(self, request, *args, **kwargs):
		# Try to dispatch to the right method; if a method doesn't exist,
		# defer to the error handler. Also defer to the error handler if the
		# request method isn't on the approved list.
		if request.method.lower() in self.http_method_names:
			handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
		else:
			handler = self.http_method_not_allowed
		return handler(request, *args, **kwargs)

	@method_decorator(never_cache)
	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		"""Logout may be done via POST."""
		auth_logout(request)
		next_page = self.get_next_page()
		if next_page:
			# Redirect to this page until the session has been cleared.
			return HttpResponseRedirect(next_page)
		# return super().post(request, *args, **kwargs)
		return HttpResponseRedirect('/')



class HomePageView(TemplateView):
	"""
	Home page with content from around the site
	"""
	template_name = "home.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		# 5 Minute Quake Guide Links
		context['guide_links'] = [
			('/quake/buy', 'Buy Quake'),
			('/quake/download', 'Download Quake'),
			('/quake/installation', 'Quake Installation'),
			('/quake/recommended_engines', 'Recommended Quake Engines'),
			('/quake/configuration', 'Quake Configuration'),
			('/tools/quake_injector', 'One-click map installation with the Quake Injector'),
			('/quaddicted.com/contribute', 'Be awesome, contribute!'),
		]

		# Guide and Help
		context['help_links'] = [
			('/help/how_to_package_and_release_a_file', 'How to package and release a file'),
			('/help/installing_custom_content', 'Installing custom content'),
			('/help/troubleshooting_common_errors', 'Troubleshooting / Common Errors'),
			('https://quakewiki.org/wiki/Easter_eggs', 'Easter eggs'),
			('/quake/cooperative', 'Cooperative Quake'),
			('/start?do=index', 'Sitemap'),
		]

		# the the four newest packages
		context['latest_pkgs'] = Package.objects.order_by('-uploaded_on')[:5]

		# get the five topics with the newest posts
		context['latest_topics'] = Topic.objects.order_by('-last_post__created')[:5]

		# Wiki highlights
		context['wiki_highlights'] = [
			('/quake/episodes_maps', 'Quake\'s Episodes and Maps'),
			('/quake/monsters', 'Quake\'s Monsters'),
			('/tronyn-reviews/start', 'Tronyn reviews'),
			('/engines/software_vs_glquake', 'Differences between software rendered Quake and GLQuake'),
			('/quake/quake_arcade_tournament_edition', 'Quake Arcade Tournament Edition'),
		]

		return context



class HomePageNewView(TemplateView):
	"""
	New home page layout and style
	"""
	template_name = "home_new.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		# 5 Minute Quake Guide Links
		context['guide_links'] = [
			('/quake/buy', 'Buy Quake'),
			('/quake/download', 'Download Quake'),
			('/quake/installation', 'Quake Installation'),
			('/quake/recommended_engines', 'Recommended Quake Engines'),
			('/quake/configuration', 'Quake Configuration'),
			('/tools/quake_injector', 'One-click map installation with the Quake Injector'),
			('/quaddicted.com/contribute', 'Be awesome, contribute!'),
		]

		# Guide and Help
		context['help_links'] = [
			('/help/how_to_package_and_release_a_file', 'How to package and release a file'),
			('/help/installing_custom_content', 'Installing custom content'),
			('/help/troubleshooting_common_errors', 'Troubleshooting / Common Errors'),
			('https://quakewiki.org/wiki/Easter_eggs', 'Easter eggs'),
			('/quake/cooperative', 'Cooperative Quake'),
			('/start?do=index', 'Sitemap'),
		]

		# the the four newest packages
		context['latest_pkgs'] = Package.objects.order_by('-uploaded_on')[:4]

		# get the five topics with the newest posts
		context['latest_topics'] = Topic.objects.order_by('-last_post__created')[:5]

		# Wiki highlights
		context['wiki_highlights'] = [
			('/quake/episodes_maps', 'Quake\'s Episodes and Maps'),
			('/quake/monsters', 'Quake\'s Monsters'),
			('/tronyn-reviews/start', 'Tronyn reviews'),
			('/engines/software_vs_glquake', 'Differences between software rendered Quake and GLQuake'),
			('/quake/quake_arcade_tournament_edition', 'Quake Arcade Tournament Edition'),
		]

		return context
