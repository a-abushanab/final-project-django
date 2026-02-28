from django import forms
from .models import Book, Author, Category


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'author', 'category', 'description', 'cover_image',
                  'isbn', 'pages', 'language', 'total_copies', 'available_copies', 'published_date')
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('name', 'bio', 'photo')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
