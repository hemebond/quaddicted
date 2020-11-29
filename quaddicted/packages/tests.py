from django.test import TestCase
from quaddicted.packages.models import Package, PackageAuthor



class PackageAuthorTestCase(TestCase):
	def setUp(self):
		for author in PackageAuthor.objects.all():
			print(author)
		PackageAuthor.objects.create(name="hemebond")
		PackageAuthor.objects.create(name="Hello World!")
		PackageAuthor.objects.create(name="Tester", slug="foobar")

	def test_slug(self):
		hemebond = PackageAuthor.objects.get(slug="hemebond")
		world = PackageAuthor.objects.get(slug="hello-world")
		tester = PackageAuthor.objects.get(slug="foobar")

		self.assertEqual(tester.name, 'Tester')



class PackageTestCase(TestCase):
	def setUp(self):
		pass
