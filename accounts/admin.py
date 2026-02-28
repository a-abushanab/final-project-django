from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import StudentProfile


# ── Profile inline inside User admin ─────────────────────────────────────────
class StudentProfileInline(admin.StackedInline):
    model              = StudentProfile
    can_delete         = False
    verbose_name_plural = 'Student Profile'
    extra              = 0
    readonly_fields    = ('joined_date', 'photo_preview')
    fields             = ('phone', 'photo', 'photo_preview', 'joined_date')

    @admin.display(description='Photo Preview')
    def photo_preview(self, obj):
        if obj and obj.pk and obj.photo:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;">',
                obj.photo.url,
            )
        return '—'


# ── Extend built-in UserAdmin ─────────────────────────────────────────────────
class CustomUserAdmin(BaseUserAdmin):
    inlines      = (StudentProfileInline,)
    list_display = ('avatar_tag', 'username', 'email', 'full_name',
                    'is_staff', 'is_active', 'date_joined')
    list_display_links = ('avatar_tag', 'username')
    list_filter  = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_per_page = 25
    ordering      = ('-date_joined',)

    @admin.display(description='')
    def avatar_tag(self, obj):
        try:
            if obj.profile.photo:
                return format_html(
                    '<img src="{}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;">',
                    obj.profile.photo.url,
                )
        except Exception:
            pass
        initial = (obj.get_full_name() or obj.username)[0].upper()
        bg = '#1565c0' if not obj.is_staff else '#6a1b9a'
        return format_html(
            '<div style="width:36px;height:36px;border-radius:50%;background:{};'
            'color:#fff;display:flex;align-items:center;justify-content:center;'
            'font-weight:700;font-size:.85rem;">{}</div>',
            bg, initial,
        )

    @admin.display(description='Full Name')
    def full_name(self, obj):
        return obj.get_full_name() or '—'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ── StudentProfile standalone ─────────────────────────────────────────────────
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display       = ('photo_tag', 'user', 'full_name', 'email', 'phone', 'joined_date')
    list_display_links = ('photo_tag', 'user')
    search_fields      = ('user__username', 'user__email',
                          'user__first_name', 'user__last_name', 'phone')
    readonly_fields    = ('joined_date', 'photo_preview')
    list_per_page      = 25
    ordering           = ('-joined_date',)
    fieldsets = (
        ('Account', {
            'fields': ('user',),
        }),
        ('Contact', {
            'fields': ('phone',),
        }),
        ('Photo', {
            'fields': ('photo', 'photo_preview'),
        }),
        ('Info', {
            'fields': ('joined_date',),
        }),
    )

    @admin.display(description='Photo')
    def photo_tag(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;">',
                obj.photo.url,
            )
        initial = (obj.user.get_full_name() or obj.user.username)[0].upper()
        return format_html(
            '<div style="width:36px;height:36px;border-radius:50%;background:#1565c0;'
            'color:#fff;display:flex;align-items:center;justify-content:center;'
            'font-weight:700;font-size:.85rem;">{}</div>',
            initial,
        )

    @admin.display(description='Full Name')
    def full_name(self, obj):
        return obj.user.get_full_name() or '—'

    @admin.display(description='Email')
    def email(self, obj):
        return obj.user.email or '—'

    @admin.display(description='Photo Preview')
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width:200px;border-radius:8px;">',
                obj.photo.url,
            )
        return '—'
