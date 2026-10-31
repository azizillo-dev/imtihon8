from django.urls import path

from .views import (
    BalancesView,
    DailyReportView,
    ExpenseCategoryReportView,
    ExpensesByCategoryView,
    IncomeCategoryReportView,
    IncomesByCategoryView,
    MonthlyReportView,
    SummaryView,
    TotalBalanceView,
    WeeklyReportView,
)


urlpatterns = [
    path("balances/", BalancesView.as_view(), name="report-balances"),
    path("total-balance/", TotalBalanceView.as_view(), name="report-total-balance"),
    path("summary/", SummaryView.as_view(), name="report-summary"),
    path("daily/", DailyReportView.as_view(), name="report-daily"),
    path("weekly/", WeeklyReportView.as_view(), name="report-weekly"),
    path("monthly/", MonthlyReportView.as_view(), name="report-monthly"),
    path("expenses-by-category/", ExpensesByCategoryView.as_view(), name="report-expenses-by-category"),
    path("expenses-by-category/<int:category_id>/", ExpenseCategoryReportView.as_view(), name="report-expense-category"),
    path("incomes-by-category/", IncomesByCategoryView.as_view(), name="report-incomes-by-category"),
    path("incomes-by-category/<int:category_id>/", IncomeCategoryReportView.as_view(), name="report-income-category"),
]
