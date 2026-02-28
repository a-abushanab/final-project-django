from django.contrib import admin
from django.utils.html import format_html
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display       = ('student', 'book', 'star_display', 'comment_preview', 'created_at')
    list_display_links = ('student', 'book')
    list_filter        = ('rating', 'created_at')
    search_fields      = ('student__username', 'student__email',
                          'book__title', 'comment')
    readonly_fields    = ('created_at', 'star_display')
    list_per_page      = 25
    date_hierarchy     = 'created_at'
    fieldsets = (
        ('Review', {
            'fields': ('student', 'book', 'rating', 'star_display', 'comment', 'created_at'),
        }),
    )

    # ── Custom columns ────────────────────────────────────────────────────────

    @admin.display(description='Rating')
    def star_display(self, obj):
        if not obj.pk or not obj.rating:
            return '—'
        color_map = {1: '#dc3545', 2: '#fd7e14', 3: '#ffc107', 4: '#20c997', 5: '#198754'}
        color  = color_map.get(obj.rating, '#888')
        stars  = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color:{};font-size:1.1rem;" title="{}/5">{}</span>'
            '&nbsp;<small style="color:#888;">({}/5)</small>',
            color, obj.rating, stars, obj.rating,
        )

    @admin.display(description='Comment')
    def comment_preview(self, obj):
        if obj.comment:
            return obj.comment[:80] + '…' if len(obj.comment) > 80 else obj.comment
        return format_html('<span style="color:#aaa;">—</span>')
