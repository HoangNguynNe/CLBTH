from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from judge.models import LeaderboardConfig
from judge.widgets import AdminHeavySelect2MultipleWidget


class LeaderboardConfigAdmin(admin.ModelAdmin):
    fields = ("is_hidden", "hidden_message", "allowed_users")
    list_display = ("get_status", "get_allowed_count")
    filter_horizontal = ("allowed_users",)

    def get_status(self, obj):
        if obj.is_hidden:
            return _("Bảng xếp hạng đã ẨN")
        return _("✓ Bảng xếp hạng đã HIỂN THỊ")

    get_status.short_description = _("Trạng thái")

    def get_allowed_count(self, obj):
        count = obj.allowed_users.count()
        if count > 0:
            return _(
                "{} người dùng có thể xem khi ẩn (bao gồm cả staff/superuser)"
            ).format(count)
        return _(
            "Không có người dùng nào được phép (staff/superuser cũng cần được thêm)"
        )

    get_allowed_count.short_description = _("Người dùng được phép")

    def has_add_permission(self, request):
        # Only allow one instance
        return not LeaderboardConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False
