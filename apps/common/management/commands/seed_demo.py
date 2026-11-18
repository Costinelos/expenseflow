from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from apps.expenses.models import Expense, ExpenseCategory

User = get_user_model()


class Command(BaseCommand):
    help = "Populates the database with demo users, categories, and sample expenses."

    def handle(self, *args, **options):
        users_data = [
            {"email": "employee@demo.ro", "role": User.Role.EMPLOYEE, "approval_limit": Decimal("0.00")},
            {"email": "manager@demo.ro", "role": User.Role.MANAGER, "approval_limit": Decimal("2500.00")},
            {"email": "finance@demo.ro", "role": User.Role.FINANCE, "approval_limit": Decimal("0.00")},
            {"email": "admin@demo.ro", "role": User.Role.ADMIN, "approval_limit": Decimal("10000.00"), "is_staff": True, "is_superuser": True},
        ]

        users = {}
        for data in users_data:
            email = data["email"]
            defaults = {k: v for k, v in data.items() if k != "email"}
            user, created = User.objects.get_or_create(email=email, defaults=defaults)
            if created:
                user.set_password("Demo1234!")
                user.save()
            users[user.role] = user

        categories_data = [
            ("Transport", Decimal("1500.00")),
            ("Cazare", Decimal("4000.00")),
            ("Protocol", Decimal("2000.00")),
            ("IT & Software", Decimal("5000.00")),
        ]

        categories = {}
        for name, budget in categories_data:
            cat, _ = ExpenseCategory.objects.get_or_create(
                name=name, defaults={"monthly_budget": budget}
            )
            categories[name] = cat

        sample_expenses = [
            {
                "user": users[User.Role.EMPLOYEE],
                "category": categories["Transport"],
                "title": "Taxi aeroport Otopeni",
                "amount": Decimal("120.00"),
                "currency": "RON",
                "expense_date": date(2026, 11, 10),
                "status": Expense.Status.APPROVED,
            },
            {
                "user": users[User.Role.EMPLOYEE],
                "category": categories["Protocol"],
                "title": "Masa client Alpha",
                "amount": Decimal("450.00"),
                "currency": "RON",
                "expense_date": date(2026, 11, 14),
                "status": Expense.Status.SUBMITTED,
            },
            {
                "user": users[User.Role.EMPLOYEE],
                "category": categories["IT & Software"],
                "title": "Abonament JetBrains",
                "amount": Decimal("650.00"),
                "currency": "RON",
                "expense_date": date(2026, 11, 16),
                "status": Expense.Status.DRAFT,
            },
        ]

        for exp in sample_expenses:
            Expense.objects.get_or_create(
                user=exp["user"],
                title=exp["title"],
                defaults=exp,
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully (password: Demo1234!)."))
