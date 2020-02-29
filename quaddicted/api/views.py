from rest_framework import generics

from quaddicted.packages.models import Package
from .serializers import PackageSerializer



class PackageListView(generics.ListAPIView):
	queryset = Package.objects.all().order_by('-created')
	serializer_class = PackageSerializer


class PackageDetailView(generics.RetrieveAPIView):
	queryset = Package.objects.filter(published=True)
	lookup_field = 'file_hash'
	serializer_class = PackageSerializer
