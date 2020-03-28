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
		print('logout GET')
		context = self.get_context_data()
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		"""Logout may be done via POST."""
		# return self.get(request, *args, **kwargs)
		print('logout POST')

		auth_logout(request)
		next_page = self.get_next_page()
		if next_page:
			# Redirect to this page until the session has been cleared.
			return HttpResponseRedirect(next_page)
		# return super().post(request, *args, **kwargs)
		return HttpResponseRedirect('/')
