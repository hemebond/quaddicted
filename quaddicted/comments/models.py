# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django_comments.abstracts import CommentAbstractModel, COMMENT_MAX_LENGTH
# import markdown2



# class QuaddictedCommentModel(CommentAbstractModel):
# 	markdown = models.TextField(_('comment'), max_length=COMMENT_MAX_LENGTH, editable=False)

# 	def save(self, *args, **kwargs):
# 		self.markdown = markdown2.markdown(self.comment)
# 		super().save(*args, **kwargs)
