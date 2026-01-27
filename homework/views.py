from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
)
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.utils.translation import gettext_lazy as _, gettext
from django.utils import timezone
from django.contrib import messages
from django.db import models
from django.db.models import Q, Count, Avg
from django.conf import settings

from homework.models import (
    HomeworkClass,
    HomeworkAssignment,
    HomeworkSubmission,
    HomeworkGrade,
    AssignmentCategory,
    SubmissionStatus,
    HomeworkJoinRequest,
    JoinRequestStatus,
    HomeworkSubmissionFile,
    HomeworkSubmissionHistory,
    ClassVisibility,
    HomeworkAssignmentImage,
    HomeworkCodeFile,
)
from homework.forms import (
    HomeworkClassForm,
    HomeworkAssignmentForm,
    HomeworkSubmissionForm,
    HomeworkFileSubmissionForm,
    HomeworkGradeForm,
)
from judge.models.notification import make_notification


class HomeworkMixin:
    def get_profile(self):
        return self.request.profile if hasattr(self.request, "profile") else None


class HomeworkClassListView(LoginRequiredMixin, HomeworkMixin, ListView):
    model = HomeworkClass
    template_name = "homework/class_list.html"
    context_object_name = "classes"

    def get_queryset(self):
        profile = self.get_profile()
        if not profile:
            return HomeworkClass.objects.none()

        return (
            HomeworkClass.objects.filter(is_active=True)
            .distinct()
            .prefetch_related("students", "co_managers")
            .order_by("-creation_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_profile()

        my_classes = []
        available_classes = []
        pending_requests = set()

        if profile:
            pending_requests = set(
                HomeworkJoinRequest.objects.filter(
                    requester=profile, status=JoinRequestStatus.PENDING
                ).values_list("homework_class_id", flat=True)
            )

        for hw_class in context["object_list"]:
            if hw_class.can_access(profile):
                my_classes.append(hw_class)
            elif hw_class.visibility != ClassVisibility.PRIVATE:
                # Only show public and request-to-join classes
                hw_class.has_pending_request = hw_class.id in pending_requests
                available_classes.append(hw_class)

        context["my_classes"] = my_classes
        context["available_classes"] = available_classes
        context["title"] = "Lớp học"
        context["page_type"] = "list"
        context["can_create_class"] = (
            self.request.user.is_staff
            or self.request.user.has_perm("homework.add_homeworkclass")
        )
        return context


class HomeworkClassDetailView(LoginRequiredMixin, HomeworkMixin, DetailView):
    model = HomeworkClass
    template_name = "homework/class_detail.html"
    context_object_name = "homework_class"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile = self.get_profile()
        if not self.object.can_access(profile):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_profile()
        is_manager = self.object.is_manager(profile)

        assignments = self.object.assignments.all()
        if not is_manager:
            assignments = assignments.filter(is_published=True)

        assignment_data = []
        for assignment in assignments:
            data = {
                "assignment": assignment,
                "is_past_deadline": assignment.is_past_deadline(),
                "submission": None,
                "grade": None,
            }
            if not is_manager:
                submission = assignment.submissions.filter(student=profile).first()
                if submission:
                    data["submission"] = submission
                    data["grade"] = submission.get_final_grade()
            else:
                data["submission_count"] = assignment.submissions.count()
                data["graded_count"] = assignment.submissions.filter(
                    status=SubmissionStatus.GRADED
                ).count()
            assignment_data.append(data)

        context["title"] = self.object.name
        context["page_type"] = "home"
        context["is_manager"] = is_manager
        context["is_creator"] = self.object.creator == profile
        context["is_student"] = self.object.is_student(profile)
        context["assignment_data"] = assignment_data
        return context


class HomeworkClassCreateView(LoginRequiredMixin, HomeworkMixin, CreateView):
    model = HomeworkClass
    form_class = HomeworkClassForm
    template_name = "homework/class_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.is_staff or request.user.has_perm("homework.add_homeworkclass")
        ):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.creator = self.get_profile()
        response = super().form_valid(form)
        messages.success(self.request, "Tạo lớp thành công!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Tạo lớp mới"
        context["page_type"] = "create"
        context["action"] = "Tạo lớp"
        return context


class HomeworkClassEditView(LoginRequiredMixin, HomeworkMixin, UpdateView):
    model = HomeworkClass
    form_class = HomeworkClassForm
    template_name = "homework/class_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_manager(self.get_profile()):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Cập nhật lớp thành công!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Sửa lớp"
        context["page_type"] = "edit"
        context["action"] = "Lưu thay đổi"
        context["homework_class"] = self.object
        context["is_manager"] = True
        context["is_creator"] = self.object.creator == self.get_profile()
        context["profile"] = self.get_profile()
        return context


class HomeworkAssignmentDetailView(LoginRequiredMixin, HomeworkMixin, DetailView):
    model = HomeworkAssignment
    template_name = "homework/assignment_detail.html"
    context_object_name = "assignment"
    pk_url_kwarg = "pk"

    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(
            HomeworkClass, slug=kwargs["class_slug"]
        )
        profile = self.get_profile()
        if not self.homework_class.can_access(profile):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return HomeworkAssignment.objects.filter(homework_class=self.homework_class)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_profile()
        is_manager = self.homework_class.is_manager(profile)

        context["title"] = self.object.title
        context["page_type"] = "assignment"
        context["homework_class"] = self.homework_class
        context["is_manager"] = is_manager
        context["is_creator"] = self.homework_class.creator == profile
        context["can_submit"] = (
            self.object.can_submit() and self.homework_class.is_student(profile)
        )
        context["is_past_deadline"] = self.object.is_past_deadline()

        if not is_manager:
            submission = self.object.submissions.filter(student=profile).first()
            context["my_submission"] = submission
            if submission:
                context["my_grade"] = submission.get_final_grade()
                # Get code files for current version
                context["my_code_files"] = submission.code_files.filter(
                    edit_version=submission.edit_count
                ).order_by("order")
        else:
            context["submissions"] = self.object.submissions.select_related(
                "student__user"
            ).all()

        return context


class HomeworkAssignmentCreateView(LoginRequiredMixin, HomeworkMixin, CreateView):
    model = HomeworkAssignment
    form_class = HomeworkAssignmentForm
    template_name = "homework/assignment_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(
            HomeworkClass, slug=kwargs["class_slug"]
        )
        if not self.homework_class.is_manager(self.get_profile()):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.homework_class = self.homework_class
        response = super().form_valid(form)
        images = self.request.FILES.getlist("assignment_images")
        for idx, image_file in enumerate(images):
            HomeworkAssignmentImage.objects.create(
                assignment=self.object,
                image=image_file,
                original_filename=image_file.name,
                order=idx,
            )

        messages.success(self.request, "Tạo bài tập thành công!")
        students = list(self.homework_class.students.all())
        if students:
            assignment = self.object
            html_link = f'<a href="{assignment.get_absolute_url()}">Bài tập mới: {assignment.title}</a> trong lớp <strong>{self.homework_class.name}</strong>'
            make_notification(students, "Homework", html_link, self.get_profile())

        return response

    def get_success_url(self):
        return reverse("homework_class_detail", args=[self.homework_class.slug])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Tạo bài tập mới"
        context["page_type"] = "create_assignment"
        context["homework_class"] = self.homework_class
        context["is_manager"] = True
        context["is_creator"] = self.homework_class.creator == self.get_profile()
        context["action"] = "Tạo bài tập"
        return context


class HomeworkAssignmentEditView(LoginRequiredMixin, HomeworkMixin, UpdateView):
    model = HomeworkAssignment
    form_class = HomeworkAssignmentForm
    template_name = "homework/assignment_form.html"
    pk_url_kwarg = "pk"

    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(
            HomeworkClass, slug=kwargs["class_slug"]
        )
        if not self.homework_class.is_manager(self.get_profile()):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return HomeworkAssignment.objects.filter(homework_class=self.homework_class)

    def get_success_url(self):
        return reverse(
            "homework_assignment_detail",
            args=[self.homework_class.slug, self.object.pk],
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        images = self.request.FILES.getlist("assignment_images")
        if images:
            max_order = (
                self.object.images.aggregate(max_order=models.Max("order"))["max_order"]
                or -1
            )

            for idx, image_file in enumerate(images):
                HomeworkAssignmentImage.objects.create(
                    assignment=self.object,
                    image=image_file,
                    original_filename=image_file.name,
                    order=max_order + idx + 1,
                )

        messages.success(self.request, "Cập nhật bài tập thành công!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Sửa bài tập"
        context["page_type"] = "edit_assignment"
        context["homework_class"] = self.homework_class
        context["is_manager"] = True
        context["is_creator"] = self.homework_class.creator == self.get_profile()
        context["action"] = "Lưu thay đổi"
        return context


class HomeworkAssignmentImageDeleteView(LoginRequiredMixin, HomeworkMixin, View):
    def post(self, request, class_slug, pk, image_id):
        homework_class = get_object_or_404(HomeworkClass, slug=class_slug)
        if not homework_class.is_manager(self.get_profile()):
            return JsonResponse(
                {"success": False, "error": "Permission denied"}, status=403
            )

        assignment = get_object_or_404(
            HomeworkAssignment, pk=pk, homework_class=homework_class
        )
        image = get_object_or_404(
            HomeworkAssignmentImage, pk=image_id, assignment=assignment
        )

        image.image.delete(save=False)
        image.delete()

        return JsonResponse({"success": True})


class HomeworkSubmitView(LoginRequiredMixin, HomeworkMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(
            HomeworkClass, slug=kwargs["class_slug"]
        )
        self.assignment = get_object_or_404(
            HomeworkAssignment, pk=kwargs["pk"], homework_class=self.homework_class
        )
        profile = self.get_profile()

        if not self.homework_class.is_student(profile):
            raise Http404()
        if not self.assignment.can_submit():
            messages.error(request, "Đã hết hạn nộp bài.")
            return redirect(self.assignment.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        profile = self.get_profile()
        existing = self.assignment.submissions.filter(student=profile).first()

        if self.assignment.category == AssignmentCategory.CODE:
            form = HomeworkSubmissionForm(instance=existing)
        else:
            form = HomeworkFileSubmissionForm(
                assignment=self.assignment, instance=existing
            )

        existing_code_files = []
        if existing and existing.pk:
            code_files = existing.code_files.filter(
                edit_version=existing.edit_count
            ).order_by("order")
            if code_files.exists():
                existing_code_files = list(
                    code_files.values("filename", "content", "language")
                )

        context = {
            "title": "Nộp bài tập",
            "page_type": "submit",
            "homework_class": self.homework_class,
            "assignment": self.assignment,
            "form": form,
            "is_edit": existing is not None,
            "is_manager": False,
            "ACE_URL": settings.ACE_URL,
            "existing_code_files": existing_code_files,
        }

        from django.shortcuts import render

        return render(request, "homework/submit.html", context)

    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        existing = self.assignment.submissions.filter(student=profile).first()

        if self.assignment.category == AssignmentCategory.CODE:
            form = HomeworkSubmissionForm(request.POST, instance=existing)

            if form.is_valid():
                import json

                is_editing = existing is not None

                submission = form.save(commit=False)
                submission.assignment = self.assignment
                submission.student = profile
                submission.status = SubmissionStatus.PENDING

                if is_editing:
                    new_version = existing.edit_count + 1
                    HomeworkSubmissionHistory.objects.create(
                        submission=existing,
                        edit_version=existing.edit_count,
                        code_content=existing.code_content,
                        code_language=existing.code_language,
                        submission_notes=existing.submission_notes,
                    )
                    submission.edit_count = new_version
                else:
                    submission.edit_count = 1
                    new_version = 1

                submission.save()
                code_files_data = request.POST.get("code_files_data", "")
                if code_files_data:
                    try:
                        code_files = json.loads(code_files_data)
                        if is_editing:
                            submission.code_files.filter(
                                edit_version=existing.edit_count
                            ).update(edit_version=existing.edit_count)
                        for idx, cf in enumerate(code_files):
                            HomeworkCodeFile.objects.create(
                                submission=submission,
                                filename=cf.get("filename", f"file{idx+1}.py"),
                                content=cf.get("content", ""),
                                language=cf.get("language", "python"),
                                order=idx,
                                edit_version=new_version,
                            )

                        if code_files:
                            submission.code_content = code_files[0].get("content", "")
                            submission.code_language = code_files[0].get(
                                "language", "python"
                            )
                            submission.save()
                    except json.JSONDecodeError:
                        pass

                if is_editing:
                    messages.success(
                        request,
                        f"Cập nhật bài nộp thành công! (Lần chỉnh sửa thứ {new_version})",
                    )
                else:
                    messages.success(request, "Nộp bài thành công!")
                return redirect(self.assignment.get_absolute_url())
        else:
            form = HomeworkFileSubmissionForm(
                assignment=self.assignment,
                data=request.POST,
                files=request.FILES,
                instance=existing,
            )

            files = request.FILES.getlist("submission_files")
            if not existing and not files:
                form.add_error(None, "Vui lòng chọn ít nhất một file.")
                allowed = self.assignment.get_allowed_extensions_list()
                max_size = self.assignment.max_file_size_mb * 1024 * 1024

                for f in files:
                    ext = f.name.split(".")[-1].lower()
                    if ext not in allowed:
                        form.add_error(
                            None,
                            f'Định dạng file "{f.name}" không được phép. Các định dạng cho phép: {", ".join(allowed)}',
                        )
                    if f.size > max_size:
                        form.add_error(
                            None,
                            f'File "{f.name}" quá lớn. Kích thước tối đa: {self.assignment.max_file_size_mb} MB',
                        )

            if form.is_valid() and not form.errors:
                is_editing = existing is not None

                if is_editing:
                    submission = existing
                    new_version = submission.edit_count + 1
                    HomeworkSubmissionHistory.objects.create(
                        submission=submission,
                        edit_version=submission.edit_count,
                        code_content=submission.code_content,
                        code_language=submission.code_language,
                        submission_notes=submission.submission_notes,
                    )
                    submission.files.filter(edit_version=submission.edit_count).update(
                        edit_version=submission.edit_count
                    )

                    submission.submission_notes = form.cleaned_data.get(
                        "submission_notes", ""
                    )
                    submission.edit_count = new_version
                    submission.status = SubmissionStatus.PENDING
                    submission.save()
                else:
                    submission = form.save(commit=False)
                    submission.assignment = self.assignment
                    submission.student = profile
                    submission.status = SubmissionStatus.PENDING
                    submission.edit_count = 1
                    submission.save()
                    new_version = 1

                for f in files:
                    HomeworkSubmissionFile.objects.create(
                        submission=submission,
                        file=f,
                        original_filename=f.name,
                        edit_version=new_version,
                    )

                if is_editing:
                    messages.success(
                        request,
                        f"Cập nhật bài nộp thành công! (Lần chỉnh sửa thứ {new_version})",
                    )
                else:
                    messages.success(request, "Nộp bài thành công!")
                return redirect(self.assignment.get_absolute_url())

        existing_code_files = []
        if existing and existing.pk:
            code_files = existing.code_files.filter(
                edit_version=existing.edit_count
            ).order_by("order")
            if code_files.exists():
                existing_code_files = list(
                    code_files.values("filename", "content", "language")
                )

        context = {
            "title": "Nộp bài tập",
            "page_type": "submit",
            "homework_class": self.homework_class,
            "assignment": self.assignment,
            "form": form,
            "is_edit": existing is not None,
            "is_manager": False,
            "ACE_URL": settings.ACE_URL,
            "existing_code_files": existing_code_files,
        }

        from django.shortcuts import render

        return render(request, "homework/submit.html", context)


class HomeworkSubmissionDetailView(LoginRequiredMixin, HomeworkMixin, DetailView):
    model = HomeworkSubmission
    template_name = "homework/submission_detail.html"
    context_object_name = "submission"
    pk_url_kwarg = "submission_pk"

    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(
            HomeworkClass, slug=kwargs["class_slug"]
        )
        self.assignment = get_object_or_404(
            HomeworkAssignment, pk=kwargs["pk"], homework_class=self.homework_class
        )
        profile = self.get_profile()

        is_manager = self.homework_class.is_manager(profile)
        self.object = self.get_object()

        if not is_manager and self.object.student != profile:
            raise Http404()

        self.is_manager = is_manager
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return HomeworkSubmission.objects.filter(assignment=self.assignment)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_profile()

        context["title"] = "Chi tiết bài nộp"
        context["page_type"] = "submission_detail"
        context["homework_class"] = self.homework_class
        context["assignment"] = self.assignment
        context["is_manager"] = self.is_manager
        context["is_creator"] = self.homework_class.creator == profile

        # Check if current manager already graded
        existing_grade = self.object.grades.filter(grader=profile).first()
        context["existing_grade"] = existing_grade
        context["can_grade"] = self.is_manager and (
            not existing_grade or self.assignment.allow_multiple_graders
        )
        context["grade_form"] = HomeworkGradeForm(instance=existing_grade)
        context["all_grades"] = self.object.grades.select_related("grader__user").all()

        context["current_code_files"] = self.object.code_files.filter(
            edit_version=self.object.edit_count
        ).order_by("order")

        context["current_files"] = self.object.files.filter(
            edit_version=self.object.edit_count
        ).order_by("id")

        context["all_files"] = self.object.files.all()

        # Get code files history grouped by version
        if self.object.edit_count > 1:
            code_files_history = {}
            for version in range(1, self.object.edit_count):
                files = self.object.code_files.filter(edit_version=version).order_by(
                    "order"
                )
                if files.exists():
                    code_files_history[version] = list(files)
            context["code_files_history"] = code_files_history

        return context


class HomeworkGradeView(LoginRequiredMixin, HomeworkMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(
            HomeworkClass, slug=kwargs["class_slug"]
        )
        self.assignment = get_object_or_404(
            HomeworkAssignment, pk=kwargs["pk"], homework_class=self.homework_class
        )
        self.submission = get_object_or_404(
            HomeworkSubmission, pk=kwargs["submission_pk"], assignment=self.assignment
        )
        profile = self.get_profile()

        if not self.homework_class.is_manager(profile):
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        existing_grade = self.submission.grades.filter(grader=profile).first()

        if existing_grade and not self.assignment.allow_multiple_graders:
            messages.error(request, "Bạn đã chấm điểm bài này rồi.")
            return redirect(
                "homework_submission_detail",
                class_slug=self.homework_class.slug,
                pk=self.assignment.pk,
                submission_pk=self.submission.pk,
            )

        form = HomeworkGradeForm(request.POST, instance=existing_grade)

        if form.is_valid():
            grade = form.save(commit=False)
            grade.submission = self.submission
            grade.grader = profile
            grade.save()
            self.submission.status = SubmissionStatus.GRADED
            self.submission.save()

            messages.success(request, "Lưu điểm thành công!")
            return redirect(
                "homework_submission_detail",
                class_slug=self.homework_class.slug,
                pk=self.assignment.pk,
                submission_pk=self.submission.pk,
            )

        messages.error(request, "Vui lòng sửa các lỗi bên dưới.")
        return redirect(
            "homework_submission_detail",
            class_slug=self.homework_class.slug,
            pk=self.assignment.pk,
            submission_pk=self.submission.pk,
        )


class HomeworkAllSubmissionsView(LoginRequiredMixin, HomeworkMixin, ListView):
    model = HomeworkSubmission
    template_name = "homework/all_submissions.html"
    context_object_name = "submissions"

    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(
            HomeworkClass, slug=kwargs["class_slug"]
        )
        self.assignment = get_object_or_404(
            HomeworkAssignment, pk=kwargs["pk"], homework_class=self.homework_class
        )
        if not self.homework_class.is_manager(self.get_profile()):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            self.assignment.submissions.select_related("student__user")
            .annotate(avg_grade=Avg("grades__score"))
            .order_by("-submission_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Tất cả bài nộp"
        context["page_type"] = "all_submissions"
        context["homework_class"] = self.homework_class
        context["assignment"] = self.assignment
        context["is_manager"] = True
        context["is_creator"] = self.homework_class.creator == self.get_profile()

        # Get students who haven't submitted
        submitted_students = self.assignment.submissions.values_list(
            "student_id", flat=True
        )
        context["not_submitted"] = self.homework_class.students.exclude(
            id__in=submitted_students
        )

        return context


class HomeworkClassStudentsView(LoginRequiredMixin, HomeworkMixin, ListView):
    template_name = "homework/class_students.html"
    context_object_name = "students"

    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(HomeworkClass, slug=kwargs["slug"])
        if not self.homework_class.is_manager(self.get_profile()):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.homework_class.students.select_related("user").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Học viên của lớp"
        context["page_type"] = "students"
        context["homework_class"] = self.homework_class
        context["is_manager"] = True
        context["is_creator"] = self.homework_class.creator == self.get_profile()
        context["co_managers"] = self.homework_class.co_managers.select_related(
            "user"
        ).all()
        return context


class HomeworkStudentDetailView(LoginRequiredMixin, HomeworkMixin, DetailView):
    template_name = "homework/student_detail.html"
    context_object_name = "student"

    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(HomeworkClass, slug=kwargs["slug"])
        if not self.homework_class.is_manager(self.get_profile()):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        from judge.models import Profile

        return get_object_or_404(Profile, id=self.kwargs["student_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object

        submissions = (
            HomeworkSubmission.objects.filter(
                assignment__homework_class=self.homework_class, student=student
            )
            .select_related("assignment")
            .prefetch_related("grades__grader__user")
            .order_by("-submission_date")
        )

        total_assignments = self.homework_class.assignments.filter(
            is_published=True
        ).count()
        submitted_count = submissions.values("assignment").distinct().count()

        all_grades = []
        total_score = 0
        graded_count = 0

        for submission in submissions:
            grade = submission.get_final_grade()
            grades = list(submission.grades.select_related("grader__user").all())
            if grade is not None:
                total_score += grade
                graded_count += 1
            all_grades.append(
                {
                    "submission": submission,
                    "assignment": submission.assignment,
                    "final_grade": grade,
                    "grades": grades,
                }
            )

        avg_score = round(total_score / graded_count, 2) if graded_count > 0 else None

        context["title"] = f"Chi tiết Học viên: {student.user.username}"
        context["page_type"] = "student_detail"
        context["homework_class"] = self.homework_class
        context["is_manager"] = True
        context["is_creator"] = self.homework_class.creator == self.get_profile()
        context["submissions_data"] = all_grades
        context["stats"] = {
            "total_assignments": total_assignments,
            "submitted_count": submitted_count,
            "graded_count": graded_count,
            "avg_score": avg_score,
            "total_score": total_score,
        }
        return context


class HomeworkRemoveStudentView(LoginRequiredMixin, HomeworkMixin, View):
    def post(self, request, *args, **kwargs):
        homework_class = get_object_or_404(HomeworkClass, slug=kwargs["slug"])
        profile = self.get_profile()

        if not homework_class.is_manager(profile):
            raise Http404()

        from judge.models import Profile

        student = get_object_or_404(Profile, id=kwargs["student_id"])

        if homework_class.students.filter(id=student.id).exists():
            homework_class.students.remove(student)
            messages.success(
                request, f"Đã xóa Học viên {student.user.username} khỏi lớp."
            )
        else:
            messages.error(request, "Học viên không tồn tại trong lớp này.")

        return redirect("homework_class_students", slug=homework_class.slug)


class HomeworkMySubmissionsView(LoginRequiredMixin, HomeworkMixin, ListView):
    model = HomeworkSubmission
    template_name = "homework/my_submissions.html"
    context_object_name = "submissions"

    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(HomeworkClass, slug=kwargs["slug"])
        if not self.homework_class.is_student(self.get_profile()):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        profile = self.get_profile()
        return (
            HomeworkSubmission.objects.filter(
                assignment__homework_class=self.homework_class, student=profile
            )
            .select_related("assignment")
            .order_by("-submission_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Bài nộp của tôi"
        context["page_type"] = "my_submissions"
        context["homework_class"] = self.homework_class
        context["is_manager"] = False
        context["is_creator"] = False
        context["is_student"] = True
        return context


class HomeworkClassDeleteView(LoginRequiredMixin, HomeworkMixin, DeleteView):
    model = HomeworkClass
    template_name = "homework/class_confirm_delete.html"
    success_url = reverse_lazy("homework_class_list")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile = self.get_profile()
        # Only creator can delete
        if self.object.creator != profile:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Đã xóa lớp học thành công!")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Xóa lớp học"
        context["homework_class"] = self.object
        return context


class HomeworkJoinRequestView(LoginRequiredMixin, HomeworkMixin, View):
    def post(self, request, *args, **kwargs):
        homework_class = get_object_or_404(HomeworkClass, slug=kwargs["slug"])
        profile = self.get_profile()

        if homework_class.can_access(profile):
            messages.error(request, "Bạn đã là thành viên của lớp này.")
            return redirect("homework_class_list")
        if homework_class.visibility == ClassVisibility.PRIVATE:
            messages.error(
                request, "Lớp này là lớp riêng tư. Bạn cần được mời để tham gia."
            )
            return redirect("homework_class_list")

        if homework_class.visibility == ClassVisibility.PUBLIC:
            homework_class.students.add(profile)
            messages.success(request, "Bạn đã tham gia lớp thành công!")
            return redirect(homework_class.get_absolute_url())

        existing_request = HomeworkJoinRequest.objects.filter(
            homework_class=homework_class,
            requester=profile,
        ).first()

        if existing_request:
            if existing_request.status == JoinRequestStatus.PENDING:
                messages.info(request, "Bạn đã gửi yêu cầu tham gia lớp này rồi.")
            elif existing_request.status == JoinRequestStatus.REJECTED:
                existing_request.status = JoinRequestStatus.PENDING
                existing_request.reviewed_by = None
                existing_request.reviewed_date = None
                existing_request.save()
                messages.success(
                    request,
                    "Đã gửi lại yêu cầu tham gia lớp. Vui lòng đợi người hỗ trợ duyệt.",
                )
            else:
                messages.info(request, "Yêu cầu của bạn đã được xử lý.")
            return redirect("homework_class_list")

        HomeworkJoinRequest.objects.create(
            homework_class=homework_class,
            requester=profile,
            status=JoinRequestStatus.PENDING,
        )

        messages.success(
            request, "Đã gửi yêu cầu tham gia lớp. Vui lòng đợi người hỗ trợ duyệt."
        )
        return redirect("homework_class_list")


class HomeworkJoinRequestsListView(LoginRequiredMixin, HomeworkMixin, ListView):
    model = HomeworkJoinRequest
    template_name = "homework/join_requests.html"
    context_object_name = "join_requests"

    def dispatch(self, request, *args, **kwargs):
        self.homework_class = get_object_or_404(HomeworkClass, slug=kwargs["slug"])
        profile = self.get_profile()
        if not self.homework_class.is_manager(profile):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            self.homework_class.join_requests.filter(status=JoinRequestStatus.PENDING)
            .select_related("requester__user")
            .order_by("-request_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Yêu cầu tham gia"
        context["page_type"] = "join_requests"
        context["homework_class"] = self.homework_class
        context["is_manager"] = True
        context["is_creator"] = self.homework_class.creator == self.get_profile()
        return context


class HomeworkApproveJoinView(LoginRequiredMixin, HomeworkMixin, View):
    def post(self, request, *args, **kwargs):
        homework_class = get_object_or_404(HomeworkClass, slug=kwargs["slug"])
        profile = self.get_profile()

        if not homework_class.is_manager(profile):
            raise Http404()

        join_request = get_object_or_404(
            HomeworkJoinRequest,
            id=kwargs["request_id"],
            homework_class=homework_class,
            status=JoinRequestStatus.PENDING,
        )

        homework_class.students.add(join_request.requester)
        join_request.status = JoinRequestStatus.APPROVED
        join_request.reviewed_by = profile
        join_request.reviewed_date = timezone.now()
        join_request.save()

        messages.success(
            request, f"Đã duyệt {join_request.requester.user.username} vào lớp."
        )
        return redirect("homework_join_requests", slug=homework_class.slug)


class HomeworkRejectJoinView(LoginRequiredMixin, HomeworkMixin, View):
    def post(self, request, *args, **kwargs):
        homework_class = get_object_or_404(HomeworkClass, slug=kwargs["slug"])
        profile = self.get_profile()

        if not homework_class.is_manager(profile):
            raise Http404()

        join_request = get_object_or_404(
            HomeworkJoinRequest,
            id=kwargs["request_id"],
            homework_class=homework_class,
            status=JoinRequestStatus.PENDING,
        )
        join_request.status = JoinRequestStatus.REJECTED
        join_request.reviewed_by = profile
        join_request.reviewed_date = timezone.now()
        join_request.save()

        messages.success(
            request, f"Đã từ chối yêu cầu của {join_request.requester.user.username}."
        )
        return redirect("homework_join_requests", slug=homework_class.slug)
