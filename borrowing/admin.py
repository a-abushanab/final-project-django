from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import BorrowRecord


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display       = ('student', 'book_link', 'borrow_date', 'due_date',
                          'return_date', 'status_badge', 'overdue_tag')
    list_display_links = ('student',)
    list_filter        = ('status', 'borrow_date', 'due_date')
    search_fields      = ('student__username', 'student__email',
                          'book__title', 'book__isbn')
    date_hierarchy     = 'borrow_date'
    readonly_fields    = ('borrow_date', 'overdue_tag')
    list_per_page      = 25
    actions            = ('action_mark_returned',)
    fieldsets = (
        ('Parties', {
            'fields': ('student', 'book'),
        }),
        ('Dates', {
            'fields': ('borrow_date', 'due_date', 'return_date'),
        }),
        ('Status', {
            'fields': ('status', 'overdue_tag'),
        }),
    )

    # ── Custom columns ────────────────────────────────────────────────────────

    @admin.display(description='Book')
    def book_link(self, obj):
        return format_html(
            '<a href="/admin/books/book/{}/change/" style="font-weight:600;">{}</a>',
            obj.book.pk, obj.book.title,
        )

    @admin.display(description='Status')
    def status_badge(self, obj):
        if obj.status == 'returned':
            return format_html(
                '<span style="background:#d1e7dd;color:#0f5132;padding:2px 12px;'
                'border-radius:20px;font-size:.78rem;font-weight:600;">Returned</span>'
            )
        if obj.is_overdue:
            return format_html(
                '<span style="background:#f8d7da;color:#842029;padding:2px 12px;'
                'border-radius:20px;font-size:.78rem;font-weight:600;">Overdue</span>'
            )
        return format_html(
            '<span style="background:#fff3cd;color:#856404;padding:2px 12px;'
            'border-radius:20px;font-size:.78rem;font-weight:600;">Borrowed</span>'
        )

    @admin.display(description='Overdue?', boolean=True)
    def overdue_tag(self, obj):
        if not obj.pk or not obj.due_date:
            return False
        return obj.is_overdue

    # ── Bulk action ───────────────────────────────────────────────────────────

    @admin.action(description='Mark selected records as Returned')
    def action_mark_returned(self, request, queryset):
        today   = timezone.now().date()
        updated = 0
        for record in queryset.filter(status='borrowed'):
            record.return_date = today
            record.status      = 'returned'
            record.save()
            record.book.available_copies += 1
            record.book.save()
            updated += 1
        self.message_user(request, f'{updated} record(s) successfully marked as returned.')
