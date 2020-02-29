default_app_config = "quaddicted.comments.apps.QuaddictedCommentsConfig"


# use a custom model for comments
# def get_model():
# 	from quaddicted_comments.models import QuaddictedCommentModel
# 	return QuaddictedCommentModel

# use a custom form for comments
def get_form():
    from .forms import QuaddictedCommentForm
    return QuaddictedCommentForm
