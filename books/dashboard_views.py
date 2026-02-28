from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from books.models import Book, Author, Category
from borrowing.models import BorrowRecord


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def dashboard(request):
    today = timezone.now().date()

    total_books = Book.objects.count()
    total_authors = Author.objects.count()
    total_categories = Category.objects.count()
    total_students = User.objects.filter(is_staff=False, is_superuser=False).count()
    active_borrowings = BorrowRecord.objects.filter(status='borrowed').count()
    overdue_borrowings = BorrowRecord.objects.filter(
        status='borrowed', due_date__lt=today
    ).count()

    top_books = (
        Book.objects.annotate(borrow_count=Count('borrow_records'))
        .order_by('-borrow_count')[:5]
    )
    top_students = (
        User.objects.annotate(borrow_count=Count('borrow_records'))
        .filter(is_staff=False)
        .order_by('-borrow_count')[:5]
    )
    recent_borrowings = BorrowRecord.objects.select_related('student', 'book').order_by('-borrow_date')[:10]

    return render(request, 'admin_dashboard/dashboard.html', {
        'total_books': total_books,
        'total_authors': total_authors,
        'total_categories': total_categories,
        'total_students': total_students,
        'active_borrowings': active_borrowings,
        'overdue_borrowings': overdue_borrowings,
        'top_books': top_books,
        'top_students': top_students,
        'recent_borrowings': recent_borrowings,
        'today': today,
    })
