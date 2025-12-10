from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from library_management.models import Book, BookComment
from library_management.forms import BookCommentForm

@login_required
@require_POST  # Chỉ chấp nhận method POST
def add_comment(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    form = BookCommentForm(request.POST)

    if form.is_valid():
        # Tạo object comment nhưng chưa lưu xuống DB (commit=False)
        comment = form.save(commit=False)
        # Gán user và book thủ công
        comment.user = request.user
        comment.book = book
        # Lưu chính thức
        comment.save()
        
        messages.success(request, _("Bình luận của bạn đã được đăng."))
    else:
        messages.error(request, _("Có lỗi xảy ra với bình luận của bạn."))

    # Quay lại trang chi tiết sách
    return redirect('catalog:book_detail', pk=book_id)
