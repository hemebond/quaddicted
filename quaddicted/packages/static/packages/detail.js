$('#flagCommentModal').on('show.bs.modal', function(event) {
	var button = $(event.relatedTarget);
	var comment_id = button.data('comment-id');
	var modal = $(this);

	var comment_author = $('#c' + comment_id).find('.comment-user').text();
	var comment_text = $('#c' + comment_id).find('blockquote').html();

	modal.find('form').attr('action', '/comments/flag/' + comment_id + '/');
	modal.find('.modal-title').text();
	modal.find('.comment-text').html(comment_text);
	modal.find('.comment-author').text(comment_author);
	modal.find("input[name='comment_id']").val(comment_id);
});

$('#flagCommentForm').submit(function(event) {
	// Stop the regular form submission
	event.preventDefault();

	var $form = $(this);
	var action = $form.attr('action');

	$.post(action, $form.serialize())
		.done(function(data) {
			// hide the current flagCommentModal and show the
			// acknowledgement popup modal
			$flagCommentModal = $('#flagCommentModal').modal('hide').on('hidden.bs.modal', function(event) {
				$ackModal = $('#ackModal');

				// use success colour for the modal
				$ackModal.find('.modal-header').addClass('bg-success text-white');
				$ackModal.find('.modal-header button').addClass('text-light');

				// update the title
				$ackModal.find('.modal-title').text('Success');
				// update the body
				$ackModal.find('.modal-body').html('<p>Post reported</p>');
				// show the modal
				$ackModal.modal('show');
			});
		});
});
