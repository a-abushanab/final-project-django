from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from .models import Book, Author, Category
from .forms import BookForm, AuthorForm, CategoryForm
from borrowing.models import BorrowRecord

SORT_OPTIONS = {
    'newest': '-created_at',
    'oldest': 'created_at',
    'rating': None,   # handled separately via annotate
}


def is_admin(user):
    return user.is_staff


def book_list(request):
    categories = Category.objects.all()
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    sort = request.GET.get('sort', 'newest')

    books = Book.objects.select_related('author', 'category').annotate(
        avg_rating=Avg('reviews__rating')
    )

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__name__icontains=query))

    if category_id:
        books = books.filter(category_id=category_id)

    if sort == 'rating':
        books = books.order_by('-avg_rating')
    elif sort == 'oldest':
        books = books.order_by('created_at')
    else:
        books = books.order_by('-created_at')
        sort = 'newest'

    paginator = Paginator(books.distinct(), 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'books/book_list.html', {
        'books': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'sort': sort,
        'total_count': paginator.count,
    })


def book_detail(request, pk):
    book = get_object_or_404(
        Book.objects.select_related('author', 'category').annotate(
            avg_rating=Avg('reviews__rating')
        ),
        pk=pk,
    )
    reviews = book.reviews.select_related('student').order_by('-created_at')

    user_borrow = None
    user_review = None
    can_review = False
    has_returned = False

    if request.user.is_authenticated and not request.user.is_staff:
        user_borrow = BorrowRecord.objects.filter(
            student=request.user, book=book, status='borrowed'
        ).first()
        user_review = reviews.filter(student=request.user).first()
        has_returned = BorrowRecord.objects.filter(
            student=request.user, book=book, status='returned'
        ).exists()
        can_review = not user_review and has_returned

    return render(request, 'books/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'user_borrow': user_borrow,
        'user_review': user_review,
        'can_review': can_review,
        'has_returned': has_returned,
    })


def author_detail_public(request, pk):
    author = get_object_or_404(Author, pk=pk)
    author_books = (
        Book.objects.filter(author=author)
        .select_related('category')
        .annotate(avg_rating=Avg('reviews__rating'))
        .order_by('-created_at')
    )
    return render(request, 'books/author_detail.html', {
        'author': author,
        'author_books': author_books,
    })


def public_category_list(request):
    categories = Category.objects.annotate(book_count=Count('books')).order_by('name')
    return render(request, 'books/public_category_list.html', {'categories': categories})


def public_author_list(request):
    authors = Author.objects.annotate(book_count=Count('books')).order_by('name')
    return render(request, 'books/public_author_list.html', {'authors': authors})


@user_passes_test(is_admin)
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Add Book'})


@user_passes_test(is_admin)
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('book_detail', pk=pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Edit Book', 'book': book})


@user_passes_test(is_admin)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


@user_passes_test(is_admin)
def author_list(request):
    authors = Author.objects.all()
    return render(request, 'books/author_list.html', {'authors': authors})


@user_passes_test(is_admin)
def author_create(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Author added successfully.')
            return redirect('author_list')
    else:
        form = AuthorForm()
    return render(request, 'books/author_form.html', {'form': form, 'title': 'Add Author'})


@user_passes_test(is_admin)
def author_edit(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, 'Author updated successfully.')
            return redirect('author_list')
    else:
        form = AuthorForm(instance=author)
    return render(request, 'books/author_form.html', {'form': form, 'title': 'Edit Author'})


@user_passes_test(is_admin)
def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        author.delete()
        messages.success(request, 'Author deleted successfully.')
        return redirect('author_list')
    return render(request, 'books/author_confirm_delete.html', {'author': author})


@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'books/category_list.html', {'categories': categories})


@user_passes_test(is_admin)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'books/category_form.html', {'form': form, 'title': 'Add Category'})


@user_passes_test(is_admin)
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'books/category_form.html', {'form': form, 'title': 'Edit Category'})


@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('category_list')
    return render(request, 'books/category_confirm_delete.html', {'category': category})
