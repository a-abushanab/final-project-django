from django.urls import path
from . import views
from borrowing import views as borrowing_views
from . import dashboard_views

urlpatterns = [
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
    path('borrowings/', borrowing_views.all_borrowings, name='all_borrowings'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/add/', views.author_create, name='author_create'),
    path('authors/<int:pk>/edit/', views.author_edit, name='author_edit'),
    path('authors/<int:pk>/delete/', views.author_delete, name='author_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
