from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from elms.views import home, contact
from books.views import public_category_list, public_author_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('contact/', contact, name='contact'),
    path('categories/', public_category_list, name='public_category_list'),
    path('authors/', public_author_list, name='public_author_list'),
    path('accounts/', include('accounts.urls')),
    path('books/', include('books.urls')),
    path('borrowing/', include('borrowing.urls')),
    path('reviews/', include('reviews.urls')),
    path('admin-panel/', include('books.admin_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
