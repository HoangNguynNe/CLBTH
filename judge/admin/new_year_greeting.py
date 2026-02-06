# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html

from judge.models import NewYearGreeting, NewYearGreetingPermission, NewYearGreetingSeen


@admin.register(NewYearGreeting)
class NewYearGreetingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "greeting_type_display",
        "title_short",
        "author_display",
        "year",
        "order",
        "is_active",
        "created_at",
    ]
    list_filter = ["greeting_type", "year", "is_active"]
    search_fields = ["title", "message", "author__username", "display_name"]
    list_editable = ["order", "is_active"]
    ordering = ["greeting_type", "order", "-created_at"]

    fieldsets = (
        (
            "Thông tin cơ bản",
            {"fields": ("greeting_type", "year", "order", "is_active")},
        ),
        ("Nội dung", {"fields": ("title", "message")}),
        (
            "Tác giả",
            {
                "fields": ("author", "display_name"),
                "description": "Để trống author nếu là lời chúc từ CLB",
            },
        ),
    )

    def greeting_type_display(self, obj):
        colors = {
            "clb_intro": "#3498db",
            "clb_wish": "#9b59b6",
            "superadmin": "#e74c3c",
            "supporter": "#2ecc71",
            "clb_ending": "#f39c12",
        }
        color = colors.get(obj.greeting_type, "#95a5a6")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_greeting_type_display(),
        )

    greeting_type_display.short_description = "Loại"
    greeting_type_display.admin_order_field = "greeting_type"

    def title_short(self, obj):
        if obj.title:
            return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message

    title_short.short_description = "Tiêu đề/Nội dung"

    def author_display(self, obj):
        return obj.get_display_author()

    author_display.short_description = "Tác giả"


@admin.register(NewYearGreetingPermission)
class NewYearGreetingPermissionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "can_send_greeting",
        "year",
        "granted_by",
        "created_at",
        "has_sent",
    ]
    list_filter = ["can_send_greeting", "year"]
    search_fields = ["user__username", "user__first_name", "granted_by__username"]
    list_editable = ["can_send_greeting"]
    autocomplete_fields = ["user", "granted_by"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Người dùng", {"fields": ("user", "year")}),
        ("Quyền hạn", {"fields": ("can_send_greeting", "granted_by")}),
    )

    def has_sent(self, obj):
        sent = NewYearGreeting.objects.filter(
            author=obj.user, greeting_type="supporter", year=obj.year
        ).exists()
        if sent:
            return format_html('<span style="color: green;">✅ Đã gửi</span>')
        return format_html('<span style="color: orange;">⏳ Chưa gửi</span>')

    has_sent.short_description = "Trạng thái"

    def save_model(self, request, obj, form, change):
        if not obj.granted_by:
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(NewYearGreetingSeen)
class NewYearGreetingSeenAdmin(admin.ModelAdmin):
    list_display = ["user", "year", "seen_at"]
    list_filter = ["year"]
    search_fields = ["user__username"]
    readonly_fields = ["user", "year", "seen_at"]
    ordering = ["-seen_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
