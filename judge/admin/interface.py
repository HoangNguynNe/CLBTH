from django.contrib import admin
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from mptt.admin import DraggableMPTTAdmin
from reversion.admin import VersionAdmin
from reversion_compare.admin import CompareVersionAdmin


from judge.dblock import LockModel
from judge.models import NavigationBar
from judge.widgets import (
    AdminHeavySelect2MultipleWidget,
    AdminHeavySelect2Widget,
    HeavyPreviewAdminPageDownWidget,
)


class NavigationBarAdmin(DraggableMPTTAdmin):
    list_display = DraggableMPTTAdmin.list_display + ("key", "linked_path")
    fields = ("key", "label", "path", "order", "regex", "parent")
    list_editable = ()  # Bug in SortableModelAdmin: 500 without list_editable being set
    mptt_level_indent = 20
    sortable = "order"

    def __init__(self, *args, **kwargs):
        super(NavigationBarAdmin, self).__init__(*args, **kwargs)
        self.__save_model_calls = 0

    def linked_path(self, obj):
        return format_html('<a href="{0}" target="_blank">{0}</a>', obj.path)

    linked_path.short_description = _("link path")

    def save_model(self, request, obj, form, change):
        self.__save_model_calls += 1
        return super(NavigationBarAdmin, self).save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        self.__save_model_calls = 0
        with NavigationBar.objects.disable_mptt_updates():
            result = super(NavigationBarAdmin, self).changelist_view(
                request, extra_context
            )
        if self.__save_model_calls:
            with LockModel(write=(NavigationBar,)):
                NavigationBar.objects.rebuild()
        return result


class BlogPostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlogPostForm, self).__init__(*args, **kwargs)
        if "authors" in self.fields:
            self.fields["authors"].widget.can_add_related = False

    class Meta:
        widgets = {
            "authors": AdminHeavySelect2MultipleWidget(
                data_view="profile_select2", attrs={"style": "width: 100%"}
            ),
            "organizations": AdminHeavySelect2MultipleWidget(
                data_view="organization_select2", attrs={"style": "width: 100%"}
            ),
        }

        if HeavyPreviewAdminPageDownWidget is not None:
            widgets["content"] = HeavyPreviewAdminPageDownWidget(
                preview=reverse_lazy("blog_preview")
            )
            widgets["summary"] = HeavyPreviewAdminPageDownWidget(
                preview=reverse_lazy("blog_preview")
            )


class BlogPostAdmin(CompareVersionAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "authors",
                    "visible",
                    "sticky",
                    "publish_on",
                    "is_organization_private",
                    "organizations",
                )
            },
        ),
        (_("Content"), {"fields": ("content", "og_image")}),
        (_("Summary"), {"classes": ("collapse",), "fields": ("summary",)}),
    )
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("id", "title", "visible", "sticky", "publish_on")
    list_display_links = ("id", "title")
    ordering = ("-publish_on",)
    form = BlogPostForm
    date_hierarchy = "publish_on"

    def has_change_permission(self, request, obj=None):
        return (
            request.user.has_perm("judge.edit_all_post")
            or request.user.has_perm("judge.change_blogpost")
            and (obj is None or obj.authors.filter(id=request.profile.id).exists())
        )


class SolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SolutionForm, self).__init__(*args, **kwargs)
        self.fields["authors"].widget.can_add_related = False

    class Meta:
        widgets = {
            "authors": AdminHeavySelect2MultipleWidget(
                data_view="profile_select2", attrs={"style": "width: 100%"}
            ),
            "problem": AdminHeavySelect2Widget(
                data_view="problem_select2", attrs={"style": "width: 250px"}
            ),
        }

        if HeavyPreviewAdminPageDownWidget is not None:
            widgets["content"] = HeavyPreviewAdminPageDownWidget(
                preview=reverse_lazy("solution_preview")
            )


class LicenseForm(ModelForm):
    class Meta:
        if HeavyPreviewAdminPageDownWidget is not None:
            widgets = {
                "text": HeavyPreviewAdminPageDownWidget(
                    preview=reverse_lazy("license_preview")
                )
            }


class LicenseAdmin(admin.ModelAdmin):
    fields = ("key", "link", "name", "display", "icon", "text")
    list_display = ("name", "key")
    form = LicenseForm


class UserListFilter(admin.SimpleListFilter):
    title = _("user")
    parameter_name = "user"

    def lookups(self, request, model_admin):
        return User.objects.filter(is_staff=True).values_list("id", "username")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id=self.value(), user__is_staff=True)
        return queryset


class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = (
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    )
    list_display = (
        "__str__",
        "action_time",
        "user",
        "content_type",
        "object_link",
        "diff_link",
    )
    search_fields = (
        "object_repr",
        "change_message",
        "user__username",
        "content_type__model",
    )
    list_filter = (UserListFilter, "content_type")
    list_display_links = None
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return obj is None and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.is_deletion():
            link = obj.object_repr
        else:
            ct = obj.content_type
            try:
                link = format_html(
                    '<a href="{1}">{0}</a>',
                    obj.object_repr,
                    reverse(
                        "admin:%s_%s_change" % (ct.app_label, ct.model),
                        args=(obj.object_id,),
                    ),
                )
            except NoReverseMatch:
                link = obj.object_repr
        return link

    object_link.admin_order_field = "object_repr"
    object_link.short_description = _("object")

    def diff_link(self, obj):
        if obj.is_deletion():
            return None
        ct = obj.content_type
        try:
            url = reverse(
                "admin:%s_%s_history" % (ct.app_label, ct.model), args=(obj.object_id,)
            )
            link = format_html('<a href="{1}">{0}</a>', _("Diff"), url)
        except NoReverseMatch:
            link = None
        return link

    diff_link.short_description = _("diff")

    def queryset(self, request):
        return super().queryset(request).prefetch_related("content_type")


class SiteMaintenanceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteMaintenanceForm, self).__init__(*args, **kwargs)

    class Meta:
        widgets = {
            "allowed_users": AdminHeavySelect2MultipleWidget(
                data_view="profile_select2", attrs={"style": "width: 100%"}
            ),
        }


class SiteMaintenanceAdmin(admin.ModelAdmin):
    form = SiteMaintenanceForm
    fieldsets = (
        (
            _("Trạng thái Website"),
            {
                "fields": ("is_closed", "closure_message"),
            },
        ),
        (
            _("Người dùng và nhóm được phép truy cập"),
            {
                "fields": ("allowed_users", "allowed_groups"),
                "description": _(
                    "Superuser luôn có quyền truy cập, không cần thêm vào đây."
                ),
            },
        ),
    )
    filter_horizontal = ("allowed_groups",)
    list_display = (
        "__str__",
        "is_closed",
        "allowed_users_count",
        "allowed_groups_count",
    )

    def allowed_users_count(self, obj):
        return obj.allowed_users.count()

    allowed_users_count.short_description = _("Số người dùng được phép")

    def allowed_groups_count(self, obj):
        return obj.allowed_groups.count()

    allowed_groups_count.short_description = _("Số nhóm được phép")

    def has_add_permission(self, request):
        from judge.models import SiteMaintenance

        if SiteMaintenance.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
