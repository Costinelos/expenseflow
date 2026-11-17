import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Expense

logger = logging.getLogger("apps.tasks")


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def notify_expense_decision(self, expense_id: str, decision: str, request_id: str | None = None):
    try:
        expense = Expense.objects.select_related("user", "approved_by").get(id=expense_id)
    except Expense.DoesNotExist:
        logger.warning(
            "task.expense_not_found expense_id=%s request_id=%s",
            expense_id,
            request_id,
        )
        return

    subject = f"[ExpenseFlow] Your expense '{expense.title}' has been {decision}"
    if decision == Expense.Status.APPROVED:
        body = (
            f"Hello,\n\n"
            f"Your expense request '{expense.title}' for {expense.amount} {expense.currency} "
            f"has been APPROVED.\n"
        )
    else:
        body = (
            f"Hello,\n\n"
            f"Your expense request '{expense.title}' for {expense.amount} {expense.currency} "
            f"has been REJECTED.\nReason: {expense.rejection_reason}\n"
        )

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[expense.user.email],
        fail_silently=False,
    )

    logger.info(
        "task.notification_sent expense_id=%s decision=%s recipient=%s request_id=%s",
        expense_id,
        decision,
        expense.user.email,
        request_id,
    )