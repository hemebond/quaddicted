from django import forms
from .models import Package, PackageScreenshot, PackageUrl, PackageAuthor
from extra_views import InlineFormSetFactory



class AuthorField(forms.CharField):
	def __init__(self, delimiter=",", **kwargs):
		self.delimiter = delimiter
		super().__init__(**kwargs)

	def to_python(self, value):
		"""Return a set of PackageAuthor objects"""
		# print("AuthorField.to_python()")
		# print(value)

		if self.disabled:
			return value

		if value in self.empty_values:
			return None
		elif isinstance(value, (list, set)):
			return value

		return [
			author
			for author
			in [
				author.strip() for author in value.split(self.delimiter)
			]
			if author
		]

	def prepare_value(self, value):
		if not value:
			return ""

		if isinstance(value, str):
			return value

		# Make a list of just the names
		author_names = [str(author) for author in value]

		# Case-insensitive sort
		sorted_author_names = sorted(author_names, key=str.casefold)

		return self.delimiter.join(sorted_author_names)



class RatingForm(forms.Form):
	score = forms.IntegerField(max_value=5, min_value=1)


class PackageEditForm(forms.ModelForm):
	authors = AuthorField(help_text="A comma-separated list of author names")

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
	authors = AuthorField(help_text="A comma-separated list of author names")

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
		model = PackageScreenshot
		# fields = [
		# 	'image',
		# ]
		fields = '__all__'


class ScreenshotInline(InlineFormSetFactory):
	model = PackageScreenshot
	# fields = [
	# 	'image',
	# ]
	fields = '__all__'


class PackageUrlInline(InlineFormSetFactory):
	model = PackageUrl
	fields = '__all__'



class PackageAuthorForm(forms.ModelForm):
	class Meta:
		model = PackageAuthor
		fields = ['name',]
