from django import forms
from .models import Package, Screenshot
from extra_views import InlineFormSetFactory
from taggit.forms import TagField, TagWidgetMixin, TagWidget


class MyTagWidgetMixin(TagWidgetMixin):
	def format_value(self, value):
		print('MyTagWidgetMixin.format_value()')
		return super().format_value(value)


class MyTagWidget(MyTagWidgetMixin, forms.TextInput):
	pass

class MyTagField(TagField):
	widget = MyTagWidget

	@property
	def value(self):
		return self.widget.format_value(super().value)


class RatingForm(forms.Form):
	score = forms.IntegerField(max_value=5, min_value=1)


class PackageEditForm(forms.ModelForm):
	class Meta:
		model = Package
		fields = [
			'name',
			'game',
			'tags',
			'authors',
			'description',
		]


class PackageCreateForm(forms.ModelForm):
	class Meta:
		model = Package
		fields = [
			'file',
			'name',
			'game',
			'tags',
			'authors',
			'description',
		]


class ScreenshotForm(forms.ModelForm):
	class Meta:
		model = Screenshot
		# fields = [
		# 	'image',
		# ]
		fields = '__all__'


class ScreenshotInline(InlineFormSetFactory):
	model = Screenshot
	# fields = [
	# 	'image',
	# ]
	fields = '__all__'
