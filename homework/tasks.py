from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from homework.models import HomeworkSubmissionFile


@shared_task
def cleanup_old_submission_files():
    retention_days = 7
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    old_files = HomeworkSubmissionFile.objects.filter(
        uploaded_date__lt=cutoff_date,
        is_deleted=False,
    ).exclude(edit_version=models.F("submission__edit_count"))

    deleted_count = 0
    for file in old_files:
        try:
            file.mark_as_deleted()
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting file {file.id}: {e}")

    return f"Deleted {deleted_count} old files"


@shared_task
def cleanup_all_old_files():
    """
    Alternative cleanup that deletes ALL files older than 7 days,
    regardless of version (but keeps record in database).
    """
    from django.db import models

    retention_days = 7
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    old_files = HomeworkSubmissionFile.objects.filter(
        uploaded_date__lt=cutoff_date,
        is_deleted=False,
    )

    deleted_count = 0
    for file in old_files:
        if file.edit_version < file.submission.edit_count:
            try:
                file.mark_as_deleted()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting file {file.id}: {e}")

    return f"Deleted {deleted_count} old files"
