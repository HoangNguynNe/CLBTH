# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
import json
from datetime import datetime

from judge.models import (
    TetWish,
    TetWishLimit,
    DEFAULT_WISH_LIMIT,
    NewYearGreeting,
    NewYearGreetingPermission,
    NewYearGreetingSeen,
)


@login_required
@require_http_methods(["GET"])
def search_users(request):
    """Tìm kiếm người dùng để gửi lời chúc"""
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"users": []})

    users = User.objects.filter(
        Q(username__icontains=query) | Q(first_name__icontains=query)
    ).exclude(id=request.user.id)[:10]

    result = []
    for user in users:
        can_send = TetWish.can_send_to(request.user, user)
        result.append(
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.first_name or user.username,
                "can_send": can_send,
            }
        )

    return JsonResponse({"users": result})


@login_required
@require_http_methods(["POST"])
def send_wish(request):
    """Gửi lời chúc Tết"""
    try:
        data = json.loads(request.body)
        receiver_id = data.get("receiver_id")
        message = data.get("message", "").strip()
        is_broadcast = data.get("is_broadcast", False)

        if not message:
            return JsonResponse({"success": False, "error": "Vui lòng nhập lời chúc"})

        if len(message) > 500:
            return JsonResponse(
                {"success": False, "error": "Lời chúc tối đa 500 ký tự"}
            )

        sender = request.user
        is_superadmin = sender.is_superuser

        # Broadcast chỉ dành cho superadmin
        if is_broadcast:
            if not is_superadmin:
                return JsonResponse(
                    {"success": False, "error": "Không có quyền gửi cho tất cả"}
                )

            # Gửi cho tất cả người dùng (trừ chính mình)
            all_users = User.objects.exclude(id=sender.id)
            created_count = 0
            for user in all_users:
                try:
                    TetWish.objects.create(
                        sender=sender,
                        receiver=user,
                        message=message,
                        is_from_superadmin=True,
                        is_broadcast=True,
                    )
                    created_count += 1
                except IntegrityError:
                    # Đã gửi cho người này rồi, bỏ qua
                    pass

            return JsonResponse(
                {
                    "success": True,
                    "message": f"Đã gửi lời chúc đến {created_count} người!",
                }
            )

        # Gửi cho 1 người cụ thể
        if not receiver_id:
            return JsonResponse({"success": False, "error": "Vui lòng chọn người nhận"})

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Người nhận không tồn tại"})

        if not TetWish.can_send_to(sender, receiver):
            if sender == receiver:
                return JsonResponse(
                    {"success": False, "error": "Không thể gửi cho chính mình"}
                )
            if TetWish.objects.filter(
                sender=sender, receiver=receiver, is_broadcast=False
            ).exists():
                return JsonResponse(
                    {"success": False, "error": "Bạn đã gửi cho người này rồi"}
                )
            user_limit = TetWishLimit.get_limit(sender)
            return JsonResponse(
                {"success": False, "error": f"Bạn đã gửi đủ {user_limit} lời chúc"}
            )

        TetWish.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            is_from_superadmin=is_superadmin,
        )

        sent_count = TetWish.get_sent_count(sender)
        user_limit = TetWishLimit.get_limit(sender)
        return JsonResponse(
            {
                "success": True,
                "message": f"Đã gửi lời chúc đến {receiver.username}!",
                "sent_count": sent_count,
                "remaining": (
                    user_limit - sent_count if not is_superadmin else "unlimited"
                ),
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Dữ liệu không hợp lệ"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_http_methods(["GET"])
def get_wishes(request):
    """Lấy danh sách lời chúc đã nhận"""
    user = request.user

    wishes = TetWish.objects.filter(receiver=user).order_by("-created_at")

    result = []
    for wish in wishes:
        result.append(
            {
                "id": wish.id,
                "sender_name": (
                    wish.sender.username
                    if wish.is_from_superadmin
                    else "Người gửi ẩn danh"
                ),
                "is_from_superadmin": wish.is_from_superadmin,
                "message": wish.message,
                "is_read": wish.is_read,
                "created_at": wish.created_at.strftime("%d/%m/%Y %H:%M"),
            }
        )

    # Đếm số lời chúc chưa đọc
    unread_count = wishes.filter(is_read=False).count()

    return JsonResponse(
        {"success": True, "wishes": result, "unread_count": unread_count}
    )


@login_required
@require_http_methods(["POST"])
def mark_wish_read(request):
    """Đánh dấu lời chúc đã đọc"""
    try:
        data = json.loads(request.body)
        wish_id = data.get("wish_id")

        wish = TetWish.objects.get(id=wish_id, receiver=request.user)
        wish.is_read = True
        wish.save()

        return JsonResponse({"success": True})
    except TetWish.DoesNotExist:
        return JsonResponse({"success": False, "error": "Không tìm thấy lời chúc"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_http_methods(["GET"])
def get_wish_stats(request):
    """Lấy thống kê gửi/nhận lời chúc"""
    user = request.user

    sent_count = TetWish.get_sent_count(user)
    received_count = TetWish.objects.filter(receiver=user).count()
    unread_count = TetWish.objects.filter(receiver=user, is_read=False).count()
    user_limit = TetWishLimit.get_limit(user)

    return JsonResponse(
        {
            "success": True,
            "sent_count": sent_count,
            "max_send": user_limit if not user.is_superuser else "unlimited",
            "can_send_more": user.is_superuser or sent_count < user_limit,
            "received_count": received_count,
            "unread_count": unread_count,
            "is_superadmin": user.is_superuser,
        }
    )


@login_required
@require_http_methods(["POST"])
def set_user_limit(request):
    """Superadmin đặt giới hạn gửi cho user"""
    if not request.user.is_superuser:
        return JsonResponse({"success": False, "error": "Không có quyền thực hiện"})

    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        max_wishes = data.get("max_wishes")

        if not user_id or max_wishes is None:
            return JsonResponse({"success": False, "error": "Thiếu thông tin"})

        try:
            max_wishes = int(max_wishes)
            if max_wishes < 0 or max_wishes > 100:
                return JsonResponse(
                    {"success": False, "error": "Giới hạn phải từ 0 đến 100"}
                )
        except ValueError:
            return JsonResponse({"success": False, "error": "Giới hạn không hợp lệ"})

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Người dùng không tồn tại"})

        TetWishLimit.set_limit(target_user, max_wishes, request.user)

        return JsonResponse(
            {
                "success": True,
                "message": f"Đã đặt giới hạn {max_wishes} lời chúc cho {target_user.username}",
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Dữ liệu không hợp lệ"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_http_methods(["GET"])
def get_user_limit(request):
    """Lấy giới hạn của một user (cho superadmin)"""
    if not request.user.is_superuser:
        return JsonResponse({"success": False, "error": "Không có quyền thực hiện"})

    user_id = request.GET.get("user_id")
    if not user_id:
        return JsonResponse({"success": False, "error": "Thiếu user_id"})

    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Người dùng không tồn tại"})

    limit = TetWishLimit.get_limit(target_user)
    sent_count = TetWish.get_sent_count(target_user)

    return JsonResponse(
        {
            "success": True,
            "user_id": target_user.id,
            "username": target_user.username,
            "max_wishes": limit,
            "sent_count": sent_count,
            "remaining": limit - sent_count,
        }
    )


# ==================== NEW YEAR GREETING MODAL API ====================


@login_required
@require_http_methods(["GET"])
def check_new_year_greeting(request):
    """Kiểm tra xem user đã xem lời chúc năm mới chưa và có nên hiển thị không"""
    current_year = datetime.now().year
    user = request.user
    is_superadmin = user.is_superuser

    # Kiểm tra quyền gửi lời chúc hỗ trợ
    can_send_supporter_greeting = NewYearGreetingPermission.can_user_send(
        user, current_year
    )
    already_sent_supporter = NewYearGreeting.objects.filter(
        author=user, greeting_type="supporter", year=current_year
    ).exists()

    # Chỉ hiển thị trong khoảng thời gian năm mới
    # Lunar New Year 2026: Feb 17 (mùng 1) - Feb 26 (mùng 10)
    # Hiển thị từ 17/02 đến 26/02/2026
    today = datetime.now()
    show_start = datetime(2026, 2, 17)
    show_end = datetime(2026, 2, 26, 23, 59, 59)

    in_time_range = show_start <= today <= show_end

    # Superadmin luôn có thể test
    if is_superadmin:
        # Kiểm tra đã xem chưa
        has_seen = NewYearGreetingSeen.objects.filter(
            user=user, year=current_year
        ).exists()
        return JsonResponse(
            {
                "success": True,
                "should_show": in_time_range and not has_seen,
                "can_test": True,
                "is_superadmin": True,
                "can_send_supporter_greeting": can_send_supporter_greeting
                and not already_sent_supporter,
                "in_time_range": in_time_range,
                "year": current_year,
            }
        )

    if not in_time_range:
        return JsonResponse(
            {
                "success": True,
                "should_show": False,
                "reason": "not_in_time_range",
                "can_send_supporter_greeting": can_send_supporter_greeting
                and not already_sent_supporter,
                "is_superadmin": False,
            }
        )

    # Kiểm tra đã xem chưa
    has_seen = NewYearGreetingSeen.objects.filter(user=user, year=current_year).exists()

    if has_seen:
        return JsonResponse(
            {
                "success": True,
                "should_show": False,
                "reason": "already_seen",
                "can_send_supporter_greeting": can_send_supporter_greeting
                and not already_sent_supporter,
                "is_superadmin": False,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "should_show": True,
            "can_send_supporter_greeting": can_send_supporter_greeting
            and not already_sent_supporter,
            "is_superadmin": False,
            "year": current_year,
        }
    )


@login_required
@require_http_methods(["GET"])
def get_new_year_greetings(request):
    """Lấy tất cả lời chúc năm mới theo thứ tự hiển thị"""
    current_year = datetime.now().year

    # Lấy lời chúc CLB intro
    clb_intro = NewYearGreeting.objects.filter(
        greeting_type="clb_intro", year=current_year, is_active=True
    ).first()

    # Lấy lời chúc CLB
    clb_wishes = list(
        NewYearGreeting.objects.filter(
            greeting_type="clb_wish", year=current_year, is_active=True
        ).order_by("order")
    )

    # Lấy lời chúc superadmin
    superadmin_wishes = list(
        NewYearGreeting.objects.filter(
            greeting_type="superadmin", year=current_year, is_active=True
        ).order_by("order")
    )

    # Lấy lời chúc hỗ trợ
    supporter_wishes = list(
        NewYearGreeting.objects.filter(
            greeting_type="supporter", year=current_year, is_active=True
        ).order_by("order")
    )

    # Lấy lời kết thúc
    clb_ending = NewYearGreeting.objects.filter(
        greeting_type="clb_ending", year=current_year, is_active=True
    ).first()

    def serialize_greeting(g):
        if not g:
            return None
        return {
            "id": g.id,
            "title": g.title,
            "message": g.message,
            "author": g.get_display_author(),
            "type": g.greeting_type,
        }

    return JsonResponse(
        {
            "success": True,
            "year": current_year,
            "greetings": {
                "intro": serialize_greeting(clb_intro),
                "clb_wishes": [serialize_greeting(w) for w in clb_wishes],
                "superadmin_wishes": [serialize_greeting(w) for w in superadmin_wishes],
                "supporter_wishes": [serialize_greeting(w) for w in supporter_wishes],
                "ending": serialize_greeting(clb_ending),
            },
        }
    )


@login_required
@require_http_methods(["POST"])
def mark_new_year_greeting_seen(request):
    """Đánh dấu đã xem lời chúc năm mới"""
    current_year = datetime.now().year

    NewYearGreetingSeen.objects.get_or_create(user=request.user, year=current_year)

    return JsonResponse({"success": True})


@login_required
@require_http_methods(["POST"])
def submit_supporter_greeting(request):
    """Hỗ trợ gửi lời chúc năm mới"""
    current_year = datetime.now().year
    user = request.user

    # Kiểm tra quyền
    if not NewYearGreetingPermission.can_user_send(user, current_year):
        return JsonResponse(
            {"success": False, "error": "Bạn không có quyền gửi lời chúc năm mới"}
        )

    # Kiểm tra đã gửi chưa
    existing = NewYearGreeting.objects.filter(
        author=user, greeting_type="supporter", year=current_year
    ).exists()

    if existing:
        return JsonResponse(
            {"success": False, "error": "Bạn đã gửi lời chúc năm mới rồi"}
        )

    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()
        display_name = data.get("display_name", "").strip()

        if not message:
            return JsonResponse({"success": False, "error": "Vui lòng nhập lời chúc"})

        if len(message) > 500:
            return JsonResponse(
                {"success": False, "error": "Lời chúc tối đa 500 ký tự"}
            )

        NewYearGreeting.objects.create(
            greeting_type="supporter",
            message=message,
            author=user,
            display_name=display_name or (user.first_name or user.username),
            year=current_year,
            is_active=True,
        )

        return JsonResponse(
            {"success": True, "message": "Đã gửi lời chúc năm mới thành công!"}
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Dữ liệu không hợp lệ"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_http_methods(["GET"])
def check_can_send_greeting(request):
    """Kiểm tra user có thể gửi lời chúc hỗ trợ không"""
    current_year = datetime.now().year
    user = request.user

    can_send = NewYearGreetingPermission.can_user_send(user, current_year)

    # Kiểm tra đã gửi chưa
    already_sent = NewYearGreeting.objects.filter(
        author=user, greeting_type="supporter", year=current_year
    ).exists()

    return JsonResponse(
        {
            "success": True,
            "can_send": can_send and not already_sent,
            "has_permission": can_send,
            "already_sent": already_sent,
        }
    )


# Superadmin: Quản lý quyền gửi lời chúc
@login_required
@require_http_methods(["POST"])
def set_greeting_permission(request):
    """Superadmin cấp quyền gửi lời chúc cho user"""
    if not request.user.is_superuser:
        return JsonResponse({"success": False, "error": "Không có quyền thực hiện"})

    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        can_send = data.get("can_send", False)
        current_year = datetime.now().year

        if not user_id:
            return JsonResponse({"success": False, "error": "Thiếu user_id"})

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Người dùng không tồn tại"})

        perm, created = NewYearGreetingPermission.objects.update_or_create(
            user=target_user,
            year=current_year,
            defaults={"can_send_greeting": can_send, "granted_by": request.user},
        )

        status = "cấp" if can_send else "thu hồi"
        return JsonResponse(
            {
                "success": True,
                "message": f"Đã {status} quyền gửi lời chúc cho {target_user.username}",
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Dữ liệu không hợp lệ"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@require_http_methods(["GET"])
def get_greeting_permissions(request):
    """Lấy danh sách user có quyền gửi lời chúc"""
    if not request.user.is_superuser:
        return JsonResponse({"success": False, "error": "Không có quyền thực hiện"})

    current_year = datetime.now().year

    permissions = NewYearGreetingPermission.objects.filter(
        year=current_year, can_send_greeting=True
    ).select_related("user", "granted_by")

    result = []
    for perm in permissions:
        # Kiểm tra đã gửi lời chúc chưa
        has_sent = NewYearGreeting.objects.filter(
            author=perm.user, greeting_type="supporter", year=current_year
        ).exists()

        result.append(
            {
                "user_id": perm.user.id,
                "username": perm.user.username,
                "display_name": perm.user.first_name or perm.user.username,
                "granted_by": perm.granted_by.username if perm.granted_by else None,
                "has_sent": has_sent,
            }
        )

    return JsonResponse({"success": True, "permissions": result})
