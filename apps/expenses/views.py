import csv
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .filters import ExpenseFilter
from .models import Expense, ExpenseCategory
from .permissions import IsManagerOrAdmin
from .serializers import ExpenseCategorySerializer, ExpenseSerializer


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.filter(is_active=True)
    serializer_class = ExpenseCategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [IsManagerOrAdmin()]


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ExpenseFilter
    search_fields = ["title", "description"]
    ordering_fields = ["amount", "expense_date", "created_at"]
    ordering = ["-expense_date"]

    def get_queryset(self):
        user = self.request.user
        if (
            getattr(user, "role", None) in ["ADMIN", "MANAGER"]
            or user.is_staff
            or user.is_superuser
        ):
            return Expense.objects.all()
        return Expense.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status in [Expense.Status.APPROVED, Expense.Status.REJECTED]:
            raise ValidationError(
                {"error": "Cannot modify an expense that has already been approved or rejected."}
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.status in [Expense.Status.APPROVED, Expense.Status.REJECTED]:
            raise ValidationError(
                {"error": "Cannot delete an expense that has already been approved or rejected."}
            )
        instance.delete()

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        expense = self.get_object()

        if expense.user != request.user:
            return Response(
                {"error": "You can only submit your own expenses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if expense.status != Expense.Status.DRAFT:
            return Response(
                {"error": f"Only DRAFT expenses can be submitted. Current status: '{expense.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expense.status = Expense.Status.SUBMITTED
        expense.save()

        serializer = self.get_serializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsManagerOrAdmin],
        url_path="approve",
    )
    def approve(self, request, pk=None):
        expense = self.get_object()
        if expense.status != Expense.Status.SUBMITTED:
            return Response(
                {"error": f"Only SUBMITTED expenses can be approved. Current status: '{expense.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if (
            getattr(user, "role", None) == "MANAGER"
            and not user.is_superuser
            and getattr(user, "approval_limit", None) is not None
            and expense.amount > user.approval_limit
        ):
            return Response(
                {
                    "error": f"Expense amount ({expense.amount} {expense.currency}) exceeds your approval limit ({user.approval_limit})."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        expense.status = Expense.Status.APPROVED
        expense.approved_by = request.user
        expense.approved_at = timezone.now()
        expense.rejection_reason = ""
        expense.save()

        serializer = self.get_serializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsManagerOrAdmin],
        url_path="reject",
    )
    def reject(self, request, pk=None):
        expense = self.get_object()
        rejection_reason = request.data.get("rejection_reason", "").strip()
        if not rejection_reason:
            return Response(
                {"error": "A rejection reason is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expense.status = Expense.Status.REJECTED
        expense.approved_by = request.user
        expense.approved_at = timezone.now()
        expense.rejection_reason = rejection_reason
        expense.save()

        serializer = self.get_serializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        totals_by_currency = (
            queryset.values("currency")
            .annotate(
                total_amount=Sum("amount"),
                count=Count("id"),
            )
            .order_by("currency")
        )

        by_status = (
            queryset.values("status")
            .annotate(
                total_amount=Sum("amount"),
                count=Count("id"),
            )
            .order_by("status")
        )

        by_category = (
            queryset.values("category__name", "category__monthly_budget")
            .annotate(
                total_amount=Sum("amount"),
                count=Count("id"),
            )
            .order_by("-total_amount")
        )

        return Response(
            {
                "total_records": queryset.count(),
                "totals_by_currency": list(totals_by_currency),
                "by_status": list(by_status),
                "by_category": list(by_category),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="expenses_report.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "ID",
            "Date",
            "Title",
            "Category",
            "Amount",
            "Currency",
            "Status",
            "Employee Email",
        ])

        for expense in queryset:
            writer.writerow([
                str(expense.id),
                expense.expense_date,
                expense.title,
                expense.category.name if expense.category else "",
                expense.amount,
                expense.currency,
                expense.status,
                expense.user.email,
            ])

        return response