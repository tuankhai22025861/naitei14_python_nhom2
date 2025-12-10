from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from library_management.models import Book, Author, Category, UserFavorite, BookItem
from django.core.paginator import Paginator
from library_management.forms import BookCommentForm
class BookListView(ListView):
    model = Book
    template_name = 'catalog/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.select_related('publisher').prefetch_related('authors', 'categories').all()

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(authors__name__icontains=search_query)
            ).distinct()

        # Category filter
        category_id = self.request.GET.get('category', '')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        return context




class BookDetailView(DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    context_object_name = 'book'

    def get_queryset(self):
        return Book.objects.select_related('publisher').prefetch_related(
            'authors', 'categories', 'items', 
            'comments', 'comments__user'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Logic đếm sách & Yêu thích (Giữ nguyên)
        items = self.object.items.all()
        context['total_items'] = items.count()
        context['available_items'] = items.filter(status=BookItem.Status.AVAILABLE).count()

        is_favorited = False
        if self.request.user.is_authenticated:
            is_favorited = UserFavorite.objects.filter(
                user=self.request.user, book=self.object
            ).exists()
        context['is_favorited'] = is_favorited

        # 2. LOGIC BÌNH LUẬN + PHÂN TRANG (MỚI)
        # Lấy tất cả comment (trừ cái đã xóa), mới nhất lên đầu
        all_comments = self.object.comments.filter(is_deleted=False).order_by('-created_at')
        
        # Tạo Paginator: 5 bình luận mỗi trang
        paginator = Paginator(all_comments, 4) 
        
        # Lấy số trang hiện tại từ URL (vd: ?page=2)
        page_number = self.request.GET.get('page')
        
        # Lấy danh sách comment của trang đó
        page_obj = paginator.get_page(page_number)
        
        # Truyền biến xuống template
        context['comments'] = page_obj       # Đây là danh sách comment của trang hiện tại
        context['paginator'] = paginator     # Đối tượng phân trang
        
        # 3. Form bình luận (Giữ nguyên)
        context['comment_form'] = BookCommentForm()
        
        return context
    
class AuthorListView(ListView):
    model = Author
    template_name = 'catalog/author_list.html'
    context_object_name = 'authors'
    paginate_by = 20

    def get_queryset(self):
        queryset = Author.objects.annotate(book_count=Count('books')).all()

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(biography__icontains=search_query)
            )

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'
    context_object_name = 'author'

    def get_queryset(self):
        return Author.objects.prefetch_related('books__categories', 'books__publisher')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.object.books.all().order_by('-publish_year')
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        queryset = Category.objects.annotate(book_count=Count('books')).filter(parent__isnull=True)

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'catalog/category_detail.html'
    context_object_name = 'category'

    def get_queryset(self):
        return Category.objects.prefetch_related('books__authors', 'books__publisher', 'children')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.object.books.all().order_by('-created_at')
        context['subcategories'] = self.object.children.annotate(book_count=Count('books')).all()
        return context
