from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.conf import settings


def site_closed(request):
    """View to display when site is in maintenance/closed mode"""
    from judge.models import SiteMaintenance

    try:
        maintenance = SiteMaintenance.get_instance()
        is_closed = maintenance.is_closed
        message = maintenance.closure_message
        can_access = maintenance.can_access(request.user)
    except Exception:
        is_closed = False
        message = _("Website đang được bảo trì. Vui lòng quay lại sau.")
        can_access = True

    if not is_closed or can_access:
        return redirect("home")

    return render(
        request,
        "site_closed.html",
        {
            "title": _("Chúng tớ sẽ quay lại sớm thôi!"),
            "message": message,
            "SITE_LONG_NAME": getattr(settings, "SITE_LONG_NAME", "Online Judge"),
        },
    )
