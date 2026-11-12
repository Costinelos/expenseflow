from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Expense, ExpenseCategory

User = get_user_model()


class ExpenseWorkflowTests(APITestCase):
    def setUp(self):
        self.employee = User.objects.create_user(
            email="angajat@expenseflow.com",
            password="parola123",
            role="EMPLOYEE",
        )
        self.manager = User.objects.create_user(
            email="manager@expenseflow.com",
            password="parola123",
            role="MANAGER",
        )
        self.category = ExpenseCategory.objects.create(
            name="IT & Software",
            monthly_budget=Decimal("1000.00"),
        )
        self.expense = Expense.objects.create(
            user=self.employee,
            category=self.category,
            title="Licenta JetBrains",
            amount=Decimal("250.00"),
            currency="RON",
            expense_date="2026-11-12",
            status=Expense.Status.DRAFT,
        )

    def test_employee_cannot_create_category(self):
        self.client.force_authenticate(user=self.employee)
        url = reverse("expenses:category-list")
        response = self.client.post(url, {"name": "Protocol", "monthly_budget": "500.00"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_category(self):
        self.client.force_authenticate(user=self.manager)
        url = reverse("expenses:category-list")
        response = self.client.post(url, {"name": "Protocol", "monthly_budget": "500.00"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employee_cannot_approve_own_expense(self):
        self.expense.status = Expense.Status.SUBMITTED
        self.expense.save()

        self.client.force_authenticate(user=self.employee)
        url = reverse("expenses:expense-approve", kwargs={"pk": self.expense.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_full_approval_workflow_and_edit_lock(self):
        self.client.force_authenticate(user=self.employee)
        submit_url = reverse("expenses:expense-submit", kwargs={"pk": self.expense.id})
        res_submit = self.client.post(submit_url)
        self.assertEqual(res_submit.status_code, status.HTTP_200_OK)
        self.assertEqual(res_submit.data["status"], Expense.Status.SUBMITTED)

        self.client.force_authenticate(user=self.manager)
        approve_url = reverse("expenses:expense-approve", kwargs={"pk": self.expense.id})
        res_approve = self.client.post(approve_url)
        self.assertEqual(res_approve.status_code, status.HTTP_200_OK)
        self.assertEqual(res_approve.data["status"], Expense.Status.APPROVED)

        self.client.force_authenticate(user=self.employee)
        detail_url = reverse("expenses:expense-detail", kwargs={"pk": self.expense.id})
        res_edit = self.client.patch(detail_url, {"amount": "999.00"})
        self.assertEqual(res_edit.status_code, status.HTTP_400_BAD_REQUEST)