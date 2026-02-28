from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Author, Category, Book

# ── Site-wide branding ────────────────────────────────────────────────────────
admin.site.site_header = 'E-Library Administration'
admin.site.site_title  = 'E-Library Admin'
admin.site.index_title = 'Library Management Dashboard'


# ── Author ────────────────────────────────────────────────────────────────────
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display       = ('photo_tag', 'name', 'book_count', 'bio_preview')
    list_display_links = ('photo_tag', 'name')
    search_fields      = ('name', 'bio')
    readonly_fields    = ('photo_preview',)
    list_per_page      = 20
    fieldsets = (
        ('Author Information', {
            'fields': ('name', 'bio'),
        }),
        ('Photo', {
            'fields': ('photo', 'photo_preview'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_book_count=Count('books'))

    @admin.display(description='Photo')
    def photo_tag(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;">',
                obj.photo.url,
            )
        initial = obj.name[0].upper() if obj.name else '?'
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;background:#1565c0;'
            'color:#fff;display:flex;align-items:center;justify-content:center;'
            'font-weight:700;font-size:.9rem;">{}</div>',
            initial,
        )

    @admin.display(description='Photo Preview')
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width:200px;border-radius:8px;">',
                obj.photo.url,
            )
        return '—'

    @admin.display(description='Books', ordering='_book_count')
    def book_count(self, obj):
        return obj._book_count

    @admin.display(description='Biography')
    def bio_preview(self, obj):
        if obj.bio:
            return obj.bio[:90] + '…' if len(obj.bio) > 90 else obj.bio
        return '—'


# ── Category ──────────────────────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'book_count', 'description_preview')
    search_fields = ('name', 'description')
    list_per_page = 20
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'description'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_book_count=Count('books'))

    @admin.display(description='Books', ordering='_book_count')
    def book_count(self, obj):
        return obj._book_count

    @admin.display(description='Description')
    def description_preview(self, obj):
        if obj.description:
            return obj.description[:90] + '…' if len(obj.description) > 90 else obj.description
        return '—'


# ── Book ──────────────────────────────────────────────────────────────────────
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display       = ('cover_tag', 'title', 'author', 'category',
                          'isbn', 'copies_display', 'avg_rating_display', 'published_date')
    list_display_links = ('cover_tag', 'title')
    list_filter        = ('category', 'language')
    search_fields      = ('title', 'isbn', 'author__name', 'description')
    autocomplete_fields = ('author', 'category')
    readonly_fields    = ('cover_preview', 'avg_rating_display', 'created_at')
    list_per_page      = 20
    date_hierarchy     = 'published_date'
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'category', 'description'),
        }),
        ('Publishing Details', {
            'fields': ('isbn', 'published_date', 'pages', 'language'),
        }),
        ('Stock', {
            'fields': ('total_copies', 'available_copies'),
        }),
        ('Cover Image', {
            'fields': ('cover_image', 'cover_preview'),
        }),
        ('Metadata', {
            'fields': ('avg_rating_display', 'created_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Cover')
    def cover_tag(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width:38px;height:54px;object-fit:cover;border-radius:4px;">',
                obj.cover_image.url,
            )
        return format_html(
            '<div style="width:38px;height:54px;background:#e3f2fd;border-radius:4px;'
            'display:flex;align-items:center;justify-content:center;color:#90b4e8;">&#128214;</div>'
        )

    @admin.display(description='Cover Preview')
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-width:220px;border-radius:8px;">',
                obj.cover_image.url,
            )
        return '—'

    @admin.display(description='Available / Total')
    def copies_display(self, obj):
        color = '#198754' if obj.available_copies > 0 else '#dc3545'
        return format_html(
            '<span style="font-weight:700;color:{};">{}</span>'
            '<span style="color:#888;"> / {}</span>',
            color, obj.available_copies, obj.total_copies,
        )

    @admin.display(description='Avg Rating')
    def avg_rating_display(self, obj):
        avg = obj.average_rating
        if avg is None:
            return '—'
        filled  = round(avg)
        stars   = '★' * filled + '☆' * (5 - filled)
        return format_html(
            '<span style="color:#f59e0b;font-size:1rem;" title="{:.1f} / 5">{}</span>'
            '&nbsp;<small style="color:#888;">{:.1f}</small>',
            avg, stars, avg,
        )
