from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from finance.models import Account, Expense, ExpenseCategory, Income, IncomeCategory
from .serializers import (
    CurrencySerializer,
    ReportDateSerializer,
    ReportFilterSerializer,
    ReportMonthSerializer,
)
from .services import convert, get_rates

date_parameter = openapi.Parameter(
    'date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date',
    description="Sana, masalan 2026-10-31. Berilmasa bugungi sana olinadi",
)

date_parameters = [
    openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date',
                      description="Boshlanish sanasi, masalan 2026-10-01"),
    openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date',
                      description="Tugash sanasi, masalan 2026-10-31"),
]

month_parameters = [
    openapi.Parameter('year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                      description="Yil, masalan 2026. Berilmasa joriy yil"),
    openapi.Parameter('month', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                      description="Oy (1-12). Berilmasa joriy oy"),
]



def filter_by_date(queryset, filters):
    if filters.get('date_from'):
        queryset = queryset.filter(created_at__date__gte=filters['date_from'])
    if filters.get('date_to'):
        queryset = queryset.filter(created_at__date__lte=filters['date_to'])
    return queryset


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=date_parameters)
    def get(self, request):
        serializer = ReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data

        incomes = filter_by_date(Income.objects.filter(user=request.user), filters)
        expenses = filter_by_date(Expense.objects.filter(user=request.user), filters)

        total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_balance = Account.objects.filter(user=request.user).aggregate(total=Sum('balance'))['total'] or Decimal('0')

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'difference': total_income - total_expense,
            'total_balance': total_balance,
        }, status=200)

class DailyReportView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[date_parameter])
    def get(self, request):
        serializer = ReportDateSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        target_date = serializer.validated_data.get('date') or timezone.localdate()

        expenses = Expense.objects.filter(user=request.user, created_at__date=target_date)
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        incomes = Income.objects.filter(user=request.user, created_at__date=target_date)
        total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')

        return Response({
            "date": target_date.isoformat(),
            "total_income": total_income,
            "total_expense": total_expense,
        })


class WeeklyReportView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[date_parameter])
    def get(self, request):
        serializer = ReportDateSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        target_date = serializer.validated_data.get('date') or timezone.localdate()

        # weekday(): dushanba = 0, yakshanba = 6
        week_start = target_date - timedelta(days=target_date.weekday())
        week_end = week_start + timedelta(days=6)

        filters = {'date_from': week_start, 'date_to': week_end}
        incomes = filter_by_date(Income.objects.filter(user=request.user), filters)
        expenses = filter_by_date(Expense.objects.filter(user=request.user), filters)

        total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')

        return Response({
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "total_income": total_income,
            "total_expense": total_expense,
            "difference": total_income - total_expense,
        })


class MonthlyReportView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=month_parameters)
    def get(self, request):
        serializer = ReportMonthSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        today = timezone.localdate()
        year = serializer.validated_data.get('year', today.year)
        month = serializer.validated_data.get('month', today.month)

        month_start = date(year, month, 1)
        month_end = date(year, month, monthrange(year, month)[1])

        filters = {'date_from': month_start, 'date_to': month_end}
        incomes = filter_by_date(Income.objects.filter(user=request.user), filters)
        expenses = filter_by_date(Expense.objects.filter(user=request.user), filters)

        total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')

        return Response({
            "month_start": month_start.isoformat(),
            "month_end": month_end.isoformat(),
            "total_income": total_income,
            "total_expense": total_expense,
            "difference": total_income - total_expense,
        })




class ExpensesByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=date_parameters)
    def get(self, request):
        serializer = ReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data

        expenses = filter_by_date(
            Expense.objects.filter(user=request.user),
            filters,
        )
        report = (
            expenses
            .values("category_id", "category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        return Response([
            {
                "category_id": item["category_id"],
                "category": item["category__name"],
                "total": item["total"],
            }
            for item in report
        ])


class ExpenseCategoryReportView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=date_parameters)
    def get(self, request, category_id):
        serializer = ReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data

        category = get_object_or_404(ExpenseCategory, id=category_id, user=request.user)
        expenses = filter_by_date(Expense.objects.filter(user=request.user, category=category), filters)
        total = expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")

        return Response({
            "category_id": category.id,
            "category": category.name,
            "total": total,
        })


class IncomesByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=date_parameters)
    def get(self, request):
        serializer = ReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data

        incomes = filter_by_date(Income.objects.filter(user=request.user), filters)
        report = (
            incomes
            .values("category_id", "category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        return Response([
            {
                "category_id": item["category_id"],
                "category": item["category__name"],
                "total": item["total"],
            }
            for item in report
        ])


class IncomeCategoryReportView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=date_parameters)
    def get(self, request, category_id):
        serializer = ReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data

        category = get_object_or_404(IncomeCategory, id=category_id, user=request.user)
        incomes = filter_by_date(Income.objects.filter(user=request.user, category=category), filters)
        total = incomes.aggregate(total=Sum("amount"))["total"] or Decimal("0")

        return Response({
            "category_id": category.id,
            "category": category.name,
            "total": total,
        })






class BalancesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = Account.objects.filter(user=request.user)

        by_currency = accounts.values('currency').annotate(total=Sum('balance')).order_by('currency')
        by_type = accounts.values('account_type', 'currency').annotate(total=Sum('balance')).order_by('account_type', 'currency')

        return Response({
            'by_currency': list(by_currency),
            'by_type': list(by_type),
        })


class TotalBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('currency', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                          enum=['UZS', 'USD', 'EUR'], description="Qaysi valyutada ko'rsatish. Berilmasa UZS"),
    ])
    def get(self, request):
        serializer = CurrencySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        target = serializer.validated_data['currency']

        try:
            rates = get_rates()
        except (OSError, ValueError, KeyError):
            return Response(
                {"detail": "Kurslarni olib bo'lmadi, keyinroq urinib ko'ring."},
                status=503,
            )

        balances = Account.objects.filter(user=request.user).values('currency').annotate(total=Sum('balance'))
        total = sum(
            (convert(item['total'], item['currency'], target, rates) for item in balances),
            Decimal('0'),
        )

        return Response({
            'currency': target,
            'total': total.quantize(Decimal('0.01')),
            'rates': {code: rate.quantize(Decimal('0.01')) for code, rate in rates.items()},
        })
