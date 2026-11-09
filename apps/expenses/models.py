import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from simple_history.models import HistoricalRecords


def expense_receipt_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"receipts/user_{instance.user_id}/expense_{instance.id}.{ext}"


class ExpenseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Category Name", max_length=100, unique=True)
    description = models.TextField("Description", blank=True)
    monthly_budget = models.DecimalField(
        "Monthly Budget",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Maximum monthly budget limit for this category (0 = unlimited).",
    )
    is_active = models.BooleanField("Is Active", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        REIMBURSED = "REIMBURSED", "Reimbursed"

    class Currency(models.TextChoices):
        RON = "RON", "Romanian Leu (RON)"
        EUR = "EUR", "Euro (EUR)"
        USD = "USD", "US Dollar (USD)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="Employee",
    )

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name="Category",
    )

    title = models.CharField("Expense Title", max_length=255)
    description = models.TextField("Description / Notes", blank=True)

    amount = models.DecimalField(
        "Amount",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(
        "Currency",
        max_length=3,
        choices=Currency.choices,
        default=Currency.RON,
    )

    expense_date = models.DateField("Expense Date")

    receipt = models.FileField(
        "Receipt / Invoice",
        upload_to=expense_receipt_upload_path,
        blank=True,
        null=True,
        help_text="Uploaded receipt or invoice file (PDF, JPG, PNG).",
    )

    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expenses",
        verbose_name="Approved / Rejected By",
    )
    rejection_reason = models.TextField("Rejection Reason", blank=True)
    approved_at = models.DateTimeField(
        "Approval / Rejection Date", null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ["-expense_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["expense_date"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.amount} {self.currency} ({self.get_status_display()})"