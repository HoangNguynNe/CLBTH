# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Giới hạn mặc định số người có thể gửi
DEFAULT_WISH_LIMIT = 7


class NewYearGreeting(models.Model):
    """Model lưu lời chúc năm mới của CLB"""

    GREETING_TYPES = [
        ("clb_intro", "Lời giới thiệu CLB"),
        ("clb_wish", "Lời chúc của CLB"),
        ("superadmin", "Lời chúc Superadmin"),
        ("supporter", "Lời chúc Hỗ trợ"),
        ("clb_ending", "Lời kết thúc CLB"),
    ]

    greeting_type = models.CharField(
        max_length=20, choices=GREETING_TYPES, verbose_name="Loại lời chúc"
    )
    title = models.CharField(max_length=200, blank=True, verbose_name="Tiêu đề")
    message = models.TextField(verbose_name="Nội dung lời chúc")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="new_year_greetings",
        verbose_name="Người viết",
    )
    display_name = models.CharField(
        max_length=100, blank=True, verbose_name="Tên hiển thị (nếu khác username)"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    year = models.PositiveIntegerField(default=2026, verbose_name="Năm")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tạo lúc")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")

    class Meta:
        verbose_name = "Lời chúc năm mới"
        verbose_name_plural = "Lời chúc năm mới"
        ordering = ["greeting_type", "order", "created_at"]

    def __str__(self):
        return f"[{self.year}] {self.get_greeting_type_display()}: {self.title or self.message[:50]}"

    def get_display_author(self):
        """Lấy tên hiển thị của người viết"""
        if self.display_name:
            return self.display_name
        if self.author:
            return self.author.first_name or self.author.username
        return "CLB Tin Học"


class NewYearGreetingPermission(models.Model):
    """Model cấu hình ai được phép gửi lời chúc năm mới hỗ trợ"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="new_year_greeting_permission",
        verbose_name="Người dùng",
    )
    can_send_greeting = models.BooleanField(
        default=False, verbose_name="Được phép gửi lời chúc"
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_permissions",
        verbose_name="Cấp bởi",
    )
    year = models.PositiveIntegerField(default=2026, verbose_name="Năm")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tạo lúc")

    class Meta:
        verbose_name = "Quyền gửi lời chúc năm mới"
        verbose_name_plural = "Quyền gửi lời chúc năm mới"
        unique_together = ["user", "year"]

    def __str__(self):
        status = "Có quyền" if self.can_send_greeting else "Không có quyền"
        return f"[{self.year}] {self.user.username}: {status}"

    @classmethod
    def can_user_send(cls, user, year=2026):
        """Kiểm tra user có quyền gửi lời chúc không"""
        if user.is_superuser:
            return True
        try:
            perm = cls.objects.get(user=user, year=year)
            return perm.can_send_greeting
        except cls.DoesNotExist:
            return False


class NewYearGreetingSeen(models.Model):
    """Theo dõi user đã xem lời chúc năm mới chưa"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="new_year_greetings_seen",
        verbose_name="Người dùng",
    )
    year = models.PositiveIntegerField(default=2026, verbose_name="Năm")
    seen_at = models.DateTimeField(auto_now_add=True, verbose_name="Xem lúc")

    class Meta:
        verbose_name = "Đã xem lời chúc năm mới"
        verbose_name_plural = "Đã xem lời chúc năm mới"
        unique_together = ["user", "year"]

    def __str__(self):
        return f"{self.user.username} đã xem lời chúc năm {self.year}"


class TetWishLimit(models.Model):
    """Model lưu giới hạn gửi lời chúc cho từng người dùng"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="tet_wish_limit",
        verbose_name="Người dùng",
    )
    max_wishes = models.PositiveIntegerField(
        default=DEFAULT_WISH_LIMIT, verbose_name="Số lời chúc tối đa"
    )
    set_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="set_limits",
        verbose_name="Người đặt giới hạn",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")

    class Meta:
        verbose_name = "Giới hạn gửi lời chúc"
        verbose_name_plural = "Giới hạn gửi lời chúc"

    def __str__(self):
        return f"{self.user.username}: {self.max_wishes} lời chúc"

    @classmethod
    def get_limit(cls, user):
        """Lấy giới hạn của user"""
        try:
            return cls.objects.get(user=user).max_wishes
        except cls.DoesNotExist:
            return DEFAULT_WISH_LIMIT

    @classmethod
    def set_limit(cls, user, max_wishes, set_by):
        """Đặt giới hạn cho user"""
        obj, created = cls.objects.update_or_create(
            user=user, defaults={"max_wishes": max_wishes, "set_by": set_by}
        )
        return obj


class TetWish(models.Model):
    """Model lưu trữ lời chúc Tết"""

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_wishes",
        verbose_name="Người gửi",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_wishes",
        verbose_name="Người nhận",
    )
    message = models.TextField(max_length=500, verbose_name="Lời chúc")
    is_from_superadmin = models.BooleanField(
        default=False, verbose_name="Từ Superadmin"
    )
    is_broadcast = models.BooleanField(default=False, verbose_name="Gửi cho tất cả")
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Thời gian gửi"
    )

    class Meta:
        verbose_name = "Lời chúc Tết"
        verbose_name_plural = "Lời chúc Tết"
        ordering = ["-created_at"]
        # Không dùng unique_together vì superadmin có thể gửi broadcast + gửi riêng

    def __str__(self):
        return (
            f"{self.sender.username} → {self.receiver.username}: {self.message[:30]}..."
        )

    @classmethod
    def get_sent_count(cls, user):
        """Đếm số người đã gửi (không tính broadcast)"""
        return (
            cls.objects.filter(sender=user, is_broadcast=False)
            .values("receiver")
            .distinct()
            .count()
        )

    @classmethod
    def can_send_to(cls, sender, receiver):
        """Kiểm tra có thể gửi cho người này không"""
        # Superadmin không bị giới hạn
        if sender.is_superuser:
            return True
        # Không gửi cho chính mình
        if sender == receiver:
            return False
        # Đã gửi cho người này chưa
        if cls.objects.filter(
            sender=sender, receiver=receiver, is_broadcast=False
        ).exists():
            return False
        # Lấy giới hạn của user
        user_limit = TetWishLimit.get_limit(sender)
        # Đã gửi đủ giới hạn chưa
        if cls.get_sent_count(sender) >= user_limit:
            return False
        return True
