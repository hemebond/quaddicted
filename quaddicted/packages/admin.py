from django.contrib import admin
from .models import Package, Rating, Screenshot, Author


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
	list_display = ('user', 'username', 'package', 'score', 'created')
	search_fields = ['user', 'username', 'package__name']
	list_filter = ('score',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
	list_display = ('name', 'file_name', 'file_hash', 'published')
	search_fields = ['name', 'file_name', 'file_hash']
	list_filter = ('published', 'game')
	actions = ['make_published',]

	def make_published(self, request, queryset):
		packages_updated = queryset.update(published=True)

		if packages_updated == 1:
			message_bit = "1 package was"
		else:
			message_bit = "%s packages were" % packages_updated

		self.message_user(request, "%s successfully published." % message_bit)

	make_published.short_description = "Publish selected packages"


@admin.register(Screenshot)
class ScreenshotAdmin(admin.ModelAdmin):
	list_display = ('package', 'image',)
