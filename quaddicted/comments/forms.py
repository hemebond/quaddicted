from django.forms import Form, ModelForm, EmailField
from django_comments.forms import CommentForm, COMMENT_MAX_LENGTH, DEFAULT_COMMENTS_TIMEOUT
from django.utils.translation import gettext_lazy as _


class QuaddictedCommentForm(CommentForm):
	email = EmailField(label=_("Email address"), required=False)
