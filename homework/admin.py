from django.contrib import admin
from homework.models import (
    HomeworkClass,
    HomeworkAssignment,
    HomeworkSubmission,
    HomeworkGrade,
)


class HomeworkAssignmentInline(admin.TabularInline):
    model = HomeworkAssignment
    extra = 0
    fields = ["title", "category", "deadline", "is_published", "points"]


@admin.register(HomeworkClass)
class HomeworkClassAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "creator",
        "is_active",
        "visibility",
        "creation_date",
        "student_count",
        "assignment_count",
    ]
    list_filter = ["is_active", "visibility", "creation_date"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["co_managers", "students"]
    inlines = [HomeworkAssignmentInline]

    def get_fields(self, request, obj=None):
        fields = ["name", "slug", "description", "is_active", "visibility"]
        if request.user.is_superuser:
            fields.insert(2, "creator")
        fields.extend(["co_managers", "students"])
        return fields

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ["creator"]

    def student_count(self, obj):
        return obj.students.count()

    student_count.short_description = "Students"

    def assignment_count(self, obj):
        return obj.assignments.count()

    assignment_count.short_description = "Assignments"


class HomeworkGradeInline(admin.TabularInline):
    model = HomeworkGrade
    extra = 0
    fields = ["grader", "score", "feedback", "graded_date"]
    readonly_fields = ["graded_date"]


@admin.register(HomeworkAssignment)
class HomeworkAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "homework_class",
        "category",
        "deadline",
        "is_published",
        "points",
        "submission_count",
    ]
    list_filter = ["homework_class", "category", "is_published", "deadline"]
    search_fields = ["title", "description"]
    date_hierarchy = "deadline"

    def submission_count(self, obj):
        return obj.submissions.count()

    submission_count.short_description = "Submissions"


@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "assignment",
        "submission_date",
        "status",
        "is_late",
        "get_grade",
    ]
    list_filter = ["status", "is_late", "submission_date", "assignment__homework_class"]
    search_fields = ["student__user__username", "assignment__title"]
    date_hierarchy = "submission_date"
    inlines = [HomeworkGradeInline]

    def get_grade(self, obj):
        grade = obj.get_final_grade()
        return f"{grade}/10" if grade is not None else "-"

    get_grade.short_description = "Grade"


@admin.register(HomeworkGrade)
class HomeworkGradeAdmin(admin.ModelAdmin):
    list_display = ["submission", "grader", "score", "graded_date"]
    list_filter = ["graded_date", "grader"]
    search_fields = ["submission__student__user__username", "grader__user__username"]
    date_hierarchy = "graded_date"
