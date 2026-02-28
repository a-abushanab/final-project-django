from django.urls import path
from . import views

urlpatterns = [
    path('borrow/<int:pk>/', views.borrow_book, name='borrow_book'),
    path('return/<int:pk>/', views.return_book, name='return_book'),
    path('my-borrowings/', views.my_borrowings, name='my_borrowings'),
    path('my-books/', views.my_books, name='my_books'),
]
