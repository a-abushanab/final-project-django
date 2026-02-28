from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Avg
from django.contrib.auth.models import User
from books.models import Book, Author


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your full name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'How can we help?'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Write your message here…'}))


def home(request):
    recent_books = Book.objects.select_related('author', 'category').order_by('-created_at')[:6]
    top_rated = (
        Book.objects.annotate(avg_rating=Avg('reviews__rating'))
        .filter(avg_rating__isnull=False)
        .select_related('author')
        .order_by('-avg_rating')[:3]
    )
    stats = {
        'total_books': Book.objects.count(),
        'total_authors': Author.objects.count(),
        'total_students': User.objects.filter(is_staff=False, is_superuser=False).count(),
    }
    return render(request, 'home.html', {
        'recent_books': recent_books,
        'top_rated': top_rated,
        'stats': stats,
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Thank you! Your message has been received. We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})
