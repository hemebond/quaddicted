from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField
from quaddicted.packages.models import Package, PackageScreenshot, PackageUrl
from django_comments.models import Comment



class URIField(serializers.URLField):
	def to_representation(self, value):
		"""
		Create a full URI if the request object is available
		"""
		value = super().to_representation(value)

		request = self.context.get('request', None)
		if request is not None:
			return request.build_absolute_uri(value)

		return value



class CommentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Comment
		fields = [
			'user_name',
			'comment',
			'submit_date',
		]



class ScreenshotSerializer(serializers.ModelSerializer):
	image = URIField(source='image.url')
	thumbnail = URIField(source='thumbnail.url')

	class Meta:
		model = PackageScreenshot
		fields = [
			'image',
			'thumbnail',
		]



class PackageUrlSerializer(serializers.ModelSerializer):
	class Meta:
		model = PackageUrl
		fields = [
			'name',
			'url',
		]



class PackageSerializer(serializers.ModelSerializer):
	authors = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='name')
	comments = serializers.HyperlinkedIdentityField(
		view_name="packages:comments",
		lookup_field="file_hash",
		lookup_url_kwarg="package_hash")
	dependencies = serializers.HyperlinkedRelatedField(
		many=True,
		view_name="packages:detail",
		lookup_field="file_hash",
		lookup_url_kwarg="package_hash",
		read_only=True)
	files = serializers.StringRelatedField(many=True)
	game = serializers.CharField(source='get_game_display')
	tags = TagListSerializerField()
	type = serializers.CharField(source='get_type_display')
	url = serializers.HyperlinkedIdentityField(
		view_name="packages:detail",
		lookup_field="file_hash",
		lookup_url_kwarg="package_hash")
	rating = serializers.DecimalField(
		max_digits=None,
		decimal_places=1)
	screenshots = ScreenshotSerializer(many=True, read_only=True)
	urls = PackageUrlSerializer(many=True, read_only=True)

	class Meta:
		model = Package
		depth = 0
		fields = [
			'authors',
			'base_dir',
			'command_line',
			'comments',
			'created',
			'dependencies',
			'file',
			'file_size',
			'files',
			'game',
			'name',
			'rating',
			'screenshots',
			'start_map',
			'tags',
			'type',
			'uploaded_on',
			'url',
			'urls',
		]
