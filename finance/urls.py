from django.urls import path

from .views import (
    AccountDetailView,
    AccountView,
    ExpenseCategoryDetailView,
    ExpenseCategoryView,
    ExpenseDetailView,
    ExpenseView,
    IncomeCategoryDetailView,
    IncomeCategoryView,
    IncomeDetailView,
    IncomeView,
)


urlpatterns = [
    path("expense-categories/", ExpenseCategoryView.as_view(), name="expense-categories"),
    path("expense-categories/<int:pk>/", ExpenseCategoryDetailView.as_view(), name="expense-category-detail"),
    path("income-categories/", IncomeCategoryView.as_view(), name="income-categories"),
    path("income-categories/<int:pk>/", IncomeCategoryDetailView.as_view(), name="income-category-detail"),
    path("accounts/", AccountView.as_view(), name="finance-accounts"),
    path("accounts/<int:pk>/", AccountDetailView.as_view(), name="finance-account-detail"),
    path("expenses/", ExpenseView.as_view(), name="finance-expenses"),
    path("expenses/<int:pk>/", ExpenseDetailView.as_view(), name="finance-expense-detail"),
    path("incomes/", IncomeView.as_view(), name="finance-incomes"),
    path("incomes/<int:pk>/", IncomeDetailView.as_view(), name="finance-income-detail"),
]
