from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, ExpenseCategoryViewSet

app_name = "expenses"

router = DefaultRouter()
router.register(r"categories", ExpenseCategoryViewSet, basename="category")
router.register(r"expenses", ExpenseViewSet, basename="expense")

urlpatterns = [
    path("", include(router.urls)),
]