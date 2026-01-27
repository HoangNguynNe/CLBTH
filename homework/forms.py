from django import forms
from django.utils.translation import gettext_lazy as _

from homework.models import (
    HomeworkClass,
    HomeworkAssignment,
    HomeworkSubmission,
    HomeworkGrade,
    AssignmentCategory,
    ClassVisibility,
)
from judge.models.profile import Profile
from judge.widgets import HeavyPreviewPageDownWidget, HeavySelect2MultipleWidget


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class HomeworkClassForm(forms.ModelForm):
    co_managers = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all(),
        required=False,
        widget=HeavySelect2MultipleWidget(
            data_view="profile_select2",
            attrs={"style": "width: 100%"},
        ),
        label=_("Hỗ trợ"),
        help_text=_("Chọn người dùng có thể hỗ trợ lớp này"),
    )

    students = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all(),
        required=False,
        widget=HeavySelect2MultipleWidget(
            data_view="profile_select2",
            attrs={"style": "width: 100%"},
        ),
        label=_("Học viên"),
        help_text=_("Chọn học viên cho lớp này"),
    )

    class Meta:
        model = HomeworkClass
        fields = [
            "name",
            "slug",
            "description",
            "image_url",
            "visibility",
            "co_managers",
            "students",
            "is_active",
        ]
        widgets = {
            "description": HeavyPreviewPageDownWidget(
                preview=_("Xem trước"),
                attrs={"style": "width: 100%; max-width: 100%"},
            ),
            "visibility": forms.RadioSelect(),
        }
        labels = {
            "name": _("Tên lớp"),
            "slug": _("Đường dẫn URL"),
            "description": _("Mô tả"),
            "image_url": _("Ảnh bìa (URL)"),
            "visibility": _("Chế độ lớp"),
            "is_active": _("Đang hoạt động"),
        }
        help_texts = {
            "visibility": _(
                "Công khai: Ai cũng có thể tham gia. Xin vào: Cần được duyệt. Riêng tư: Chỉ được mời."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Nhập tên lớp")}
        )
        self.fields["slug"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("ten-lop")}
        )
        self.fields["image_url"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("https://example.com/image.png")}
        )

    def clean(self):
        cleaned_data = super().clean()
        co_managers = cleaned_data.get("co_managers", [])
        students = cleaned_data.get("students", [])
        if co_managers and students:
            overlap = set(co_managers) & set(students)
            if overlap:
                usernames = [p.user.username for p in overlap]
                raise forms.ValidationError(
                    _("Người dùng không thể vừa là hỗ trợ vừa là học viên: %(users)s"),
                    params={"users": ", ".join(usernames)},
                )

        return cleaned_data


EXTENSION_CHOICES = [
    ("py", "Python (.py)"),
    ("cpp", "C++ (.cpp)"),
    ("c", "C (.c)"),
    ("java", "Java (.java)"),
    ("txt", "Text (.txt)"),
    ("pdf", "PDF (.pdf)"),
    ("png", "PNG Image (.png)"),
    ("jpg", "JPG Image (.jpg)"),
    ("jpeg", "JPEG Image (.jpeg)"),
    ("zip", "ZIP Archive (.zip)"),
    ("rar", "RAR Archive (.rar)"),
]


class HomeworkAssignmentForm(forms.ModelForm):
    extension_choices = forms.MultipleChoiceField(
        choices=EXTENSION_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "extension-checkbox-list"}),
        required=False,
        label=_("Định dạng file cho phép"),
    )
    custom_extensions = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ví dụ: doc,docx,xlsx",
            }
        ),
        label=_("Định dạng khác"),
        help_text=_("Nhập các định dạng khác, phân cách bằng dấu phẩy"),
    )

    class Meta:
        model = HomeworkAssignment
        fields = [
            "title",
            "description",
            "category",
            "deadline",
            "allow_late_submission",
            "allow_multiple_graders",
            "max_file_size_mb",
            "points",
            "is_published",
            "is_graded",
            "order",
        ]
        widgets = {
            "description": HeavyPreviewPageDownWidget(
                preview=_("Xem trước"),
                attrs={"style": "width: 100%; max-width: 100%"},
            ),
            "deadline": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "title": _("Tiêu đề bài tập"),
            "description": _("Mô tả đề bài"),
            "category": _("Loại nộp bài"),
            "deadline": _("Hạn nộp"),
            "allow_late_submission": _("Cho phép nộp muộn"),
            "allow_multiple_graders": _("Cho phép nhiều người chấm"),
            "max_file_size_mb": _("Kích thước file tối đa (MB)"),
            "points": _("Điểm tối đa"),
            "is_published": _("Công khai"),
            "is_graded": _("Có chấm điểm"),
            "order": _("Thứ tự hiển thị"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Nhập tiêu đề bài tập")}
        )
        self.fields["max_file_size_mb"].widget.attrs.update({"class": "form-control"})
        self.fields["points"].widget.attrs.update(
            {"class": "form-control", "step": "0.5"}
        )
        self.fields["order"].widget.attrs.update({"class": "form-control"})

        if self.instance and self.instance.deadline:
            self.initial["deadline"] = self.instance.deadline.strftime("%Y-%m-%dT%H:%M")
        if self.instance and self.instance.pk and self.instance.allowed_extensions:
            existing_exts = [
                ext.strip() for ext in self.instance.allowed_extensions.split(",")
            ]
            known_exts = [ext for ext, _ in EXTENSION_CHOICES]

            selected = [ext for ext in existing_exts if ext in known_exts]
            custom = [ext for ext in existing_exts if ext not in known_exts]

            self.initial["extension_choices"] = selected
            self.initial["custom_extensions"] = ",".join(custom)

    def clean(self):
        cleaned_data = super().clean()
        selected_exts = cleaned_data.get("extension_choices", [])
        custom_exts = cleaned_data.get("custom_extensions", "")

        all_exts = list(selected_exts)
        if custom_exts:
            custom_list = [
                ext.strip().lower() for ext in custom_exts.split(",") if ext.strip()
            ]
            all_exts.extend(custom_list)

        cleaned_data["allowed_extensions"] = (
            ",".join(all_exts)
            if all_exts
            else "py,cpp,c,java,txt,pdf,png,jpg,jpeg,zip,rar"
        )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.allowed_extensions = self.cleaned_data.get("allowed_extensions", "")
        if commit:
            instance.save()
        return instance


class HomeworkSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ["code_content", "code_language", "submission_notes"]
        widgets = {
            "code_content": forms.Textarea(
                attrs={
                    "class": "form-control code-editor",
                    "rows": 20,
                    "placeholder": _("Dán code của bạn vào đây..."),
                }
            ),
            "submission_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Ghi chú cho bài nộp (không bắt buộc)..."),
                }
            ),
        }
        labels = {
            "code_content": _("Code"),
            "code_language": _("Ngôn ngữ lập trình"),
            "submission_notes": _("Ghi chú"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code_language"].widget.attrs.update({"class": "form-control"})


class HomeworkFileSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ["submission_notes"]
        widgets = {
            "submission_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Ghi chú cho bài nộp (không bắt buộc)..."),
                }
            ),
        }
        labels = {
            "submission_notes": _("Ghi chú"),
        }

    def __init__(self, assignment=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assignment = assignment


class HomeworkGradeForm(forms.ModelForm):
    SCORE_CHOICES = [(i, str(i)) for i in range(0, 11)]

    class Meta:
        model = HomeworkGrade
        fields = ["score", "feedback"]
        widgets = {
            "feedback": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": _("Nhận xét cho học viên..."),
                }
            ),
        }
        labels = {
            "score": _("Điểm"),
            "feedback": _("Nhận xét"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["score"] = forms.ChoiceField(
            choices=self.SCORE_CHOICES,
            widget=forms.Select(
                attrs={
                    "class": "form-control score-select",
                }
            ),
            label=_("Điểm (0-10)"),
        )
