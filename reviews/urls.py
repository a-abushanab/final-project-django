from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_reviews, name='public_reviews'),
    path('books/<int:pk>/review/', views.add_review, name='add_review'),
]
