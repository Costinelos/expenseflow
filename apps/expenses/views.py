from rest_framework import viewsets, permissions
from .models import Expense, ExpenseCategory
from .serializers import ExpenseSerializer, ExpenseCategorySerializer
from .filters import ExpenseFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.filter(is_active=True)
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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