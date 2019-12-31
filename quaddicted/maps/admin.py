from django.contrib import admin

# Register your models here.

from .models import Map, Tag, MapFile, Screenshot, Author, MapPackage, Demo

@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
	ordering = ['name']

	search_fields = ['name']

admin.site.register(Tag)
admin.site.register(Author)

@admin.register(Demo)
class DemoAdmin(admin.ModelAdmin):
	ordering = ['-created']


@admin.register(Screenshot)
class ScreenshotAdmin(admin.ModelAdmin):
	list_display = ('map', 'image')
	search_fields = ['map__name', 'image']


@admin.register(MapPackage)
class MapPackageAdmin(admin.ModelAdmin):
	list_display = ('file_name', 'file_hash')


@admin.register(MapFile)
class MapFileAdmin(admin.ModelAdmin):
	list_display = ('map', 'name')
