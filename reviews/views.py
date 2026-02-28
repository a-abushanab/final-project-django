from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from books.models import Book
from borrowing.models import BorrowRecord
from .models import Review
from .forms import ReviewForm


def public_reviews(request):
    reviews = Review.objects.select_related('student', 'book').order_by('-created_at')
    paginator = Paginator(reviews, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'reviews/public_reviews.html', {
        'reviews': page_obj,
        'total_count': paginator.count,
    })


@login_required
def add_review(request, pk):
    book = get_object_or_404(Book, pk=pk)

    has_returned = BorrowRecord.objects.filter(
        student=request.user, book=book, status='returned'
    ).exists()
    if not has_returned:
        messages.error(request, 'You can only review books you have borrowed and returned.')
        return redirect('book_detail', pk=pk)

    already_reviewed = Review.objects.filter(student=request.user, book=book).exists()
    if already_reviewed:
        messages.warning(request, 'You have already reviewed this book.')
        return redirect('book_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.book = book
            review.save()
            messages.success(request, 'Your review has been submitted. Thank you!')
            return redirect('book_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {'form': form, 'book': book})
