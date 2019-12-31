from django.forms import Form, ModelForm, EmailField
from django_comments.forms import CommentForm
from django.utils.translation import gettext_lazy as _


# class CommentForm(ModelForm):
# 	class Meta:
# 		model = Comment
# 		fields = ['name', 'comment']
# 		# fields = '__all__'

# 	def clean(self):
# 		cleaned_data = super().clean()

# 		name = cleaned_data.get('name', None)

# 		if self.user_id:
# 			print('got user %s' % self.user_id)


class CommentFormSimple(CommentForm):
	email = EmailField(label=_("Email address"), required=False)
