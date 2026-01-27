import os
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.conf import settings

from judge.models.profile import Profile


class ClassVisibility(models.TextChoices):
    PUBLIC = "PU", _("Public")
    REQUEST = "RQ", _("Request to join")
    PRIVATE = "PR", _("Private")


def homework_file_path(instance, filename):
    ext = filename.split(".")[-1]
    new_filename = (
        f"submission_{instance.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    )
    return os.path.join(
        "homework_submissions",
        str(instance.assignment.homework_class.id),
        str(instance.assignment.id),
        new_filename,
    )


class HomeworkClass(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name=_("class name"),
    )
    slug = models.SlugField(
        max_length=128,
        verbose_name=_("class slug"),
        help_text=_("Class name shown in URL"),
        unique=True,
        validators=[
            RegexValidator("^[-a-zA-Z0-9]+$", _("Only alphanumeric and hyphens"))
        ],
    )
    description = models.TextField(
        verbose_name=_("class description"),
        blank=True,
    )
    image_url = models.CharField(
        verbose_name=_("class image URL"),
        default="",
        max_length=300,
        blank=True,
    )
    creator = models.ForeignKey(
        Profile,
        verbose_name=_("assistant manager"),
        on_delete=models.CASCADE,
        related_name="created_homework_classes",
    )
    co_managers = models.ManyToManyField(
        Profile,
        verbose_name=_("co-managers"),
        related_name="co_managed_homework_classes",
        blank=True,
        help_text=_("Users who can manage this class"),
    )
    students = models.ManyToManyField(
        Profile,
        verbose_name=_("students"),
        related_name="enrolled_homework_classes",
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("is active"),
        default=True,
    )
    visibility = models.CharField(
        max_length=2,
        choices=ClassVisibility.choices,
        default=ClassVisibility.REQUEST,
        verbose_name=_("visibility"),
        help_text=_(
            "Public: anyone can join. Request: need approval. Private: invite only."
        ),
    )
    creation_date = models.DateTimeField(
        verbose_name=_("creation date"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("homework class")
        verbose_name_plural = _("homework classes")
        ordering = ["-creation_date"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("homework_class_detail", args=[self.slug])

    def is_manager(self, profile):
        """Check if user is creator or co-manager."""
        if not profile:
            return False
        return (
            self.creator == profile or self.co_managers.filter(id=profile.id).exists()
        )

    def is_student(self, profile):
        """Check if user is a student in this class."""
        if not profile:
            return False
        return self.students.filter(id=profile.id).exists()

    def can_access(self, profile):
        """Check if user can access this class."""
        return self.is_manager(profile) or self.is_student(profile)

    def pending_join_requests_count(self):
        """Get count of pending join requests."""
        return self.join_requests.filter(status="PE").count()


class JoinRequestStatus(models.TextChoices):
    PENDING = "PE", _("Pending")
    APPROVED = "AP", _("Approved")
    REJECTED = "RE", _("Rejected")


class HomeworkJoinRequest(models.Model):
    homework_class = models.ForeignKey(
        HomeworkClass,
        verbose_name=_("class"),
        on_delete=models.CASCADE,
        related_name="join_requests",
    )
    requester = models.ForeignKey(
        Profile,
        verbose_name=_("requester"),
        on_delete=models.CASCADE,
        related_name="homework_join_requests",
    )
    status = models.CharField(
        max_length=2,
        choices=JoinRequestStatus.choices,
        default=JoinRequestStatus.PENDING,
        verbose_name=_("status"),
    )
    request_date = models.DateTimeField(
        verbose_name=_("request date"),
        auto_now_add=True,
    )
    reviewed_by = models.ForeignKey(
        Profile,
        verbose_name=_("reviewed by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_join_requests",
    )
    reviewed_date = models.DateTimeField(
        verbose_name=_("reviewed date"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("join request")
        verbose_name_plural = _("join requests")
        ordering = ["-request_date"]
        unique_together = ["homework_class", "requester"]

    def __str__(self):
        return f"{self.requester} -> {self.homework_class}"


class AssignmentCategory(models.TextChoices):
    CODE = "CODE", _("Code")
    IMAGE = "IMAGE", _("Image/File")


class HomeworkAssignment(models.Model):
    homework_class = models.ForeignKey(
        HomeworkClass,
        verbose_name=_("class"),
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    title = models.CharField(
        max_length=256,
        verbose_name=_("assignment title"),
    )
    description = models.TextField(
        verbose_name=_("assignment description"),
        help_text=_("Detailed assignment description/problem statement"),
    )
    category = models.CharField(
        max_length=10,
        choices=AssignmentCategory.choices,
        default=AssignmentCategory.CODE,
        verbose_name=_("submission type"),
    )
    creation_date = models.DateTimeField(
        verbose_name=_("creation date"),
        auto_now_add=True,
    )
    deadline = models.DateTimeField(
        verbose_name=_("deadline"),
    )
    allow_late_submission = models.BooleanField(
        verbose_name=_("allow late submission"),
        default=False,
    )
    allow_multiple_graders = models.BooleanField(
        verbose_name=_("allow multiple graders"),
        default=False,
        help_text=_("Allow multiple managers to grade the same submission"),
    )
    max_file_size_mb = models.PositiveIntegerField(
        verbose_name=_("max file size (MB)"),
        default=10,
    )
    allowed_extensions = models.CharField(
        max_length=256,
        verbose_name=_("allowed file extensions"),
        default="py,cpp,c,java,txt,zip,rar,png,jpg,jpeg,pdf",
        help_text=_("Comma-separated list of allowed file extensions"),
    )
    points = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name=_("maximum points"),
        default=10.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    is_published = models.BooleanField(
        verbose_name=_("is published"),
        default=True,
    )
    is_graded = models.BooleanField(
        verbose_name=_("is graded"),
        default=True,
        help_text=_("Whether this assignment will be graded"),
    )
    order = models.PositiveIntegerField(
        verbose_name=_("order"),
        default=0,
    )

    class Meta:
        verbose_name = _("homework assignment")
        verbose_name_plural = _("homework assignments")
        ordering = ["order", "-creation_date"]

    def __str__(self):
        return f"{self.homework_class.name} - {self.title}"

    def get_absolute_url(self):
        return reverse(
            "homework_assignment_detail", args=[self.homework_class.slug, self.id]
        )

    def is_past_deadline(self):
        return timezone.now() > self.deadline

    def can_submit(self):
        if not self.is_past_deadline():
            return True
        return self.allow_late_submission

    def get_allowed_extensions_list(self):
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]


def assignment_image_upload_path(instance, filename):
    return f"assignment_images/{instance.assignment.id}/{filename}"


class HomeworkAssignmentImage(models.Model):
    assignment = models.ForeignKey(
        HomeworkAssignment,
        verbose_name=_("assignment"),
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        upload_to=assignment_image_upload_path,
        verbose_name=_("image"),
    )
    original_filename = models.CharField(
        max_length=256,
        verbose_name=_("original filename"),
    )
    uploaded_date = models.DateTimeField(
        verbose_name=_("uploaded date"),
        auto_now_add=True,
    )
    order = models.PositiveIntegerField(
        verbose_name=_("order"),
        default=0,
    )

    class Meta:
        verbose_name = _("assignment image")
        verbose_name_plural = _("assignment images")
        ordering = ["order", "uploaded_date"]

    def __str__(self):
        return self.original_filename


class SubmissionStatus(models.TextChoices):
    PENDING = "PE", _("Pending")
    GRADED = "GR", _("Graded")
    RETURNED = "RE", _("Returned for revision")


class HomeworkSubmission(models.Model):
    assignment = models.ForeignKey(
        HomeworkAssignment,
        verbose_name=_("assignment"),
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    student = models.ForeignKey(
        Profile,
        verbose_name=_("student"),
        on_delete=models.CASCADE,
        related_name="homework_submissions",
    )
    submission_date = models.DateTimeField(
        verbose_name=_("submission date"),
        auto_now_add=True,
    )
    updated_date = models.DateTimeField(
        verbose_name=_("last updated"),
        auto_now=True,
    )

    code_content = models.TextField(
        verbose_name=_("code content"),
        blank=True,
    )
    code_language = models.CharField(
        max_length=50,
        verbose_name=_("programming language"),
        blank=True,
        default="python",
    )
    submission_file = models.FileField(
        upload_to="homework_submissions/",
        verbose_name=_("submission file"),
        blank=True,
        null=True,
    )
    original_filename = models.CharField(
        max_length=256,
        verbose_name=_("original filename"),
        blank=True,
    )
    status = models.CharField(
        max_length=2,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.PENDING,
        verbose_name=_("status"),
    )
    is_late = models.BooleanField(
        verbose_name=_("submitted late"),
        default=False,
    )
    submission_notes = models.TextField(
        verbose_name=_("student notes"),
        blank=True,
        help_text=_("Optional notes from the student"),
    )
    edit_count = models.PositiveIntegerField(
        verbose_name=_("edit count"),
        default=0,
        help_text=_("Number of times this submission has been edited"),
    )

    class Meta:
        verbose_name = _("homework submission")
        verbose_name_plural = _("homework submissions")
        ordering = ["-submission_date"]

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"

    def save(self, *args, **kwargs):
        if self.assignment.is_past_deadline():
            self.is_late = True
        super().save(*args, **kwargs)

    def get_final_grade(self):
        grades = self.grades.all()
        if not grades.exists():
            return None
        if self.assignment.allow_multiple_graders and grades.count() > 1:
            total = sum(g.score for g in grades)
            return round(total / grades.count(), 2)
        return grades.first().score


class HomeworkCodeFile(models.Model):
    submission = models.ForeignKey(
        HomeworkSubmission,
        verbose_name=_("submission"),
        on_delete=models.CASCADE,
        related_name="code_files",
    )
    filename = models.CharField(
        max_length=256,
        verbose_name=_("filename"),
        default="main.py",
    )
    content = models.TextField(
        verbose_name=_("code content"),
        blank=True,
    )
    language = models.CharField(
        max_length=50,
        verbose_name=_("programming language"),
        default="python",
    )
    order = models.PositiveIntegerField(
        verbose_name=_("order"),
        default=0,
    )
    created_date = models.DateTimeField(
        verbose_name=_("created date"),
        auto_now_add=True,
    )
    updated_date = models.DateTimeField(
        verbose_name=_("updated date"),
        auto_now=True,
    )
    edit_version = models.PositiveIntegerField(
        verbose_name=_("edit version"),
        default=1,
    )

    class Meta:
        verbose_name = _("code file")
        verbose_name_plural = _("code files")
        ordering = ["order", "created_date"]

    def __str__(self):
        return self.filename


def submission_file_upload_path(instance, filename):
    username = instance.submission.student.user.username
    class_slug = instance.submission.assignment.homework_class.slug
    assignment_id = instance.submission.assignment.id
    return f"homework_submissions/{username}/{class_slug}/{assignment_id}/{filename}"


class HomeworkSubmissionFile(models.Model):
    submission = models.ForeignKey(
        HomeworkSubmission,
        verbose_name=_("submission"),
        on_delete=models.CASCADE,
        related_name="files",
    )
    file = models.FileField(
        upload_to=submission_file_upload_path,
        verbose_name=_("file"),
        blank=True,
        null=True,
    )
    original_filename = models.CharField(
        max_length=256,
        verbose_name=_("original filename"),
    )
    uploaded_date = models.DateTimeField(
        verbose_name=_("uploaded date"),
        auto_now_add=True,
    )
    is_deleted = models.BooleanField(
        verbose_name=_("file deleted"),
        default=False,
        help_text=_("File has been automatically deleted after retention period"),
    )
    deleted_date = models.DateTimeField(
        verbose_name=_("deleted date"),
        null=True,
        blank=True,
    )

    edit_version = models.PositiveIntegerField(
        verbose_name=_("edit version"),
        default=1,
    )

    class Meta:
        verbose_name = _("submission file")
        verbose_name_plural = _("submission files")
        ordering = ["uploaded_date"]

    def __str__(self):
        return self.original_filename

    def is_image(self):
        ext = self.original_filename.split(".")[-1].lower()
        return ext in ["png", "jpg", "jpeg", "gif", "webp"]

    def mark_as_deleted(self):
        if self.file:
            try:
                self.file.delete(save=False)
            except Exception:
                pass
        self.file = None
        self.is_deleted = True
        self.deleted_date = timezone.now()
        self.save()


class HomeworkSubmissionHistory(models.Model):
    submission = models.ForeignKey(
        HomeworkSubmission,
        verbose_name=_("submission"),
        on_delete=models.CASCADE,
        related_name="history",
    )
    edit_version = models.PositiveIntegerField(
        verbose_name=_("edit version"),
    )
    edited_date = models.DateTimeField(
        verbose_name=_("edited date"),
        auto_now_add=True,
    )
    code_content = models.TextField(
        verbose_name=_("code content"),
        blank=True,
    )
    code_language = models.CharField(
        max_length=50,
        verbose_name=_("programming language"),
        blank=True,
    )
    submission_notes = models.TextField(
        verbose_name=_("notes"),
        blank=True,
    )

    class Meta:
        verbose_name = _("submission history")
        verbose_name_plural = _("submission histories")
        ordering = ["-edit_version"]
        unique_together = ["submission", "edit_version"]

    def __str__(self):
        return f"{self.submission} - v{self.edit_version}"

    def get_files(self):
        """Get files associated with this edit version."""
        return self.submission.files.filter(edit_version=self.edit_version)


class HomeworkGrade(models.Model):
    submission = models.ForeignKey(
        HomeworkSubmission,
        verbose_name=_("submission"),
        on_delete=models.CASCADE,
        related_name="grades",
    )
    grader = models.ForeignKey(
        Profile,
        verbose_name=_("grader"),
        on_delete=models.CASCADE,
        related_name="graded_homeworks",
    )
    score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_("score"),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    feedback = models.TextField(
        verbose_name=_("feedback"),
        blank=True,
    )
    graded_date = models.DateTimeField(
        verbose_name=_("graded date"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("homework grade")
        verbose_name_plural = _("homework grades")
        ordering = ["-graded_date"]
        unique_together = ["submission", "grader"]

    def __str__(self):
        return f"{self.submission} - {self.score}/10"
