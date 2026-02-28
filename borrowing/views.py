from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from books.models import Book
from .models import BorrowRecord


MAX_BORROW_LIMIT = 5


def is_admin(user):
    return user.is_staff


@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        if book.available_copies <= 0:
            messages.error(request, 'Sorry, no copies of this book are currently available.')
            return redirect('book_detail', pk=pk)

        already_borrowed = BorrowRecord.objects.filter(
            student=request.user, book=book, status='borrowed'
        ).exists()
        if already_borrowed:
            messages.warning(request, 'You already have this book borrowed.')
            return redirect('book_detail', pk=pk)

        active_count = BorrowRecord.objects.filter(
            student=request.user, status='borrowed'
        ).count()
        if active_count >= MAX_BORROW_LIMIT:
            messages.error(
                request,
                f'You have reached the maximum limit of {MAX_BORROW_LIMIT} borrowed books. '
                'Please return a book before borrowing another.'
            )
            return redirect('book_detail', pk=pk)

        due = timezone.now().date() + timedelta(days=14)
        BorrowRecord.objects.create(student=request.user, book=book, due_date=due)
        book.available_copies -= 1
        book.save()
        messages.success(request, f'You have borrowed "{book.title}". Please return it by {due}.')

    return redirect('book_detail', pk=pk)


@login_required
def return_book(request, pk):
    record = get_object_or_404(BorrowRecord, pk=pk, student=request.user, status='borrowed')

    if request.method == 'POST':
        record.return_date = timezone.now().date()
        record.status = 'returned'
        record.save()
        record.book.available_copies += 1
        record.book.save()
        messages.success(request, f'You have returned "{record.book.title}". Thank you!')

    return redirect('book_detail', pk=record.book.pk)


@login_required
def my_borrowings(request):
    records = BorrowRecord.objects.filter(
        student=request.user
    ).select_related('book__author').order_by('-borrow_date')
    status_filter = request.GET.get('status', '')
    if status_filter in ('borrowed', 'returned'):
        records = records.filter(status=status_filter)
    return render(request, 'borrowing/my_borrowings.html', {'records': records})


@login_required
def my_books(request):
    active = BorrowRecord.objects.filter(
        student=request.user, status='borrowed'
    ).select_related('book__author', 'book__category').order_by('due_date')
    today = timezone.now().date()
    return render(request, 'borrowing/my_books.html', {
        'active': active,
        'today': today,
        'max_limit': MAX_BORROW_LIMIT,
    })


@user_passes_test(is_admin)
def all_borrowings(request):
    records = BorrowRecord.objects.select_related('student', 'book').order_by('-borrow_date')
    status_filter = request.GET.get('status', '')
    if status_filter in ('borrowed', 'returned'):
        records = records.filter(status=status_filter)
    today = timezone.now().date()
    return render(request, 'borrowing/all_borrowings.html', {
        'records': records,
        'status_filter': status_filter,
        'today': today,
    })
