from django.contrib import admin
# from django_comments.admin import CommentsAdmin
# from django_comments.models import Comment as DCComment
from django_comments.models import CommentFlag
# from .models import QuaddictedCommentModel


# admin.site.register(QuaddictedCommentModel, CommentsAdmin)
# admin.site.register(DCComment, CommentsAdmin)

@admin.register(CommentFlag)
class CommentFlagAdmin(admin.ModelAdmin):
	list_display = ('user', 'flag', 'flag_date')
