from decimal import Decimal
from rest_framework import serializers

from apps.users.serializers import UserSerializer
from .models import Expense, ExpenseCategory


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = [
            "id",
            "name",
            "description",
            "monthly_budget",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ExpenseSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "user",
            "user_details",
            "category",
            "category_name",
            "title",
            "description",
            "amount",
            "currency",
            "expense_date",
            "receipt",
            "status",
            "status_display",
            "approved_by",
            "rejection_reason",
            "approved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "status",
            "approved_by",
            "rejection_reason",
            "approved_at",
            "created_at",
            "updated_at",
        ]

    def validate_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Amount must be strictly greater than 0.00.")
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)