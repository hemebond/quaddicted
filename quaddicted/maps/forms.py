from django.forms import Form, ModelForm, EmailField
from django_comments.forms import CommentForm
from django.utils.translation import gettext_lazy as _


class CommentFormSimple(CommentForm):
	email = EmailField(label=_("Email address"), required=False)
