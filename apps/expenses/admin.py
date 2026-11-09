from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Expense, ExpenseCategory


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "monthly_budget", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(Expense)
class ExpenseAdmin(SimpleHistoryAdmin):
    list_display = (
        "title",
        "user",
        "category",
        "amount",
        "currency",
        "status",
        "expense_date",
        "approved_by",
    )
    list_filter = ("status", "currency", "category", "expense_date")
    search_fields = ("title", "description", "user__email")
    readonly_fields = ("created_at", "updated_at", "approved_at")
    raw_id_fields = ("user", "approved_by")