from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from library_management.models import UserFavorite, Book

@login_required
def favorite_books(request):
    """
    Trang hiển thị danh sách sách user đã thêm vào yêu thích.
    """
    user = request.user
    favorites = (
        UserFavorite.objects
        .filter(user=user)
        .select_related("book", "book__publisher")
        .order_by("-created_at")
    )
    context = {
        "user": user,
        "favorites": favorites,
    }
    return render(request, "library_utilities/favorites.html", context)

@login_required
def add_to_favorites(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    fav, created = UserFavorite.objects.get_or_create(
        user=request.user,
        book=book
    )
    if created:
        messages.success(request, _("Đã thêm sách vào danh sách yêu thích!"))
    else:
        messages.info(request, _("Cuốn sách này đã có trong danh sách yêu thích của bạn."))
    
    return redirect('catalog:book_detail', pk=book_id)

@login_required
def remove_from_favorites(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    deleted_count, deleted_info = UserFavorite.objects.filter(
        user=request.user,
        book=book
    ).delete()

    if deleted_count > 0:
        # Bây giờ hàm _() sẽ hoạt động bình thường
        messages.success(request, _("Đã bỏ sách khỏi danh sách yêu thích."))
    else:
        messages.warning(request, _("Sách này không có trong danh sách yêu thích của bạn."))

    return redirect('catalog:book_detail', pk=book_id)
