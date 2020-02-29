from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from quaddicted.packages.models import Package



class PackageSerializer(serializers.ModelSerializer):
	authors = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='name',
	)
	tags = TagListSerializerField()

	class Meta:
		model = Package
		depth = 1
		fields = [
			'name',
			'file',
			'file_name',
			'file_hash',
			'file_size',
			'created',
			'game',
			'rating',
			'authors',
			'tags',
		]
