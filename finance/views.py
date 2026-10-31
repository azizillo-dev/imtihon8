from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Account, Expense, ExpenseCategory, Income, IncomeCategory
from .serializers import (
    AccountSerializer,
    ExpenseCategorySerializer,
    ExpenseSerializer,
    IncomeCategorySerializer,
    IncomeSerializer,
)


class ExpenseCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = ExpenseCategory.objects.filter(user=request.user)
        return Response(ExpenseCategorySerializer(categories, many=True).data)

    @swagger_auto_schema(request_body=ExpenseCategorySerializer)
    def post(self, request):
        serializer = ExpenseCategorySerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class IncomeCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = IncomeCategory.objects.filter(user=request.user)
        return Response(IncomeCategorySerializer(categories, many=True).data)

    @swagger_auto_schema(request_body=IncomeCategorySerializer)
    def post(self, request):
        serializer = IncomeCategorySerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=AccountSerializer)
    def post(self, request):
        serializer = AccountSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        return Response(AccountSerializer(account).data, status=201)

    def get(self, request):
        accounts = Account.objects.filter(user=request.user)
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data, status=200)


class ExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ExpenseSerializer)
    def post(self, request):
        serializer = ExpenseSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        expense = serializer.save()
        return Response(ExpenseSerializer(expense).data, status=201)

    def get(self, request):
        expenses = Expense.objects.filter(user=request.user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=200)


class IncomeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=IncomeSerializer)
    def post(self, request):
        serializer = IncomeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        income = serializer.save()
        return Response(IncomeSerializer(income).data, status=201)

    def get(self, request):
        incomes = Income.objects.filter(user=request.user)
        serializer = IncomeSerializer(incomes, many=True)
        return Response(serializer.data, status=200)





class ExpenseCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        category = get_object_or_404(ExpenseCategory, id=pk, user=request.user)
        return Response(ExpenseCategorySerializer(category).data, status=200)

    @swagger_auto_schema(request_body=ExpenseCategorySerializer)
    def put(self, request, pk):
        category = get_object_or_404(ExpenseCategory, id=pk, user=request.user)
        serializer = ExpenseCategorySerializer(category, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        category = get_object_or_404(ExpenseCategory, id=pk, user=request.user)
        if Expense.objects.filter(category=category).exists():
            return Response(
                {"detail": "Bu kategoriyada xarajatlar bor, avval ularni o'chiring."},
                status=400,
            )
        category.delete()
        return Response(status=204)


class IncomeCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        category = get_object_or_404(IncomeCategory, id=pk, user=request.user)
        return Response(IncomeCategorySerializer(category).data, status=200)

    @swagger_auto_schema(request_body=IncomeCategorySerializer)
    def put(self, request, pk):
        category = get_object_or_404(IncomeCategory, id=pk, user=request.user)
        serializer = IncomeCategorySerializer(category, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        category = get_object_or_404(IncomeCategory, id=pk, user=request.user)
        if Income.objects.filter(category=category).exists():
            return Response(
                {"detail": "Bu kategoriyada daromadlar bor, avval ularni o'chiring."},
                status=400,
            )
        category.delete()
        return Response(status=204)


class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        account = get_object_or_404(Account, id=pk, user=request.user)
        return Response(AccountSerializer(account).data, status=200)

    @swagger_auto_schema(request_body=AccountSerializer)
    def put(self, request, pk):
        account = get_object_or_404(Account, id=pk, user=request.user)
        serializer = AccountSerializer(account, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        account = get_object_or_404(Account, id=pk, user=request.user)
        account.delete()
        return Response(status=204)


class ExpenseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        expense = get_object_or_404(Expense, id=pk, user=request.user)
        return Response(ExpenseSerializer(expense).data, status=200)

    @swagger_auto_schema(request_body=ExpenseSerializer)
    def put(self, request, pk):
        expense = get_object_or_404(Expense, id=pk, user=request.user)
        serializer = ExpenseSerializer(expense, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        expense = get_object_or_404(Expense, id=pk, user=request.user)
        with transaction.atomic():
            account = expense.account
            account.balance += expense.amount
            account.save(update_fields=['balance'])
            expense.delete()
        return Response(status=204)


class IncomeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        income = get_object_or_404(Income, id=pk, user=request.user)
        return Response(IncomeSerializer(income).data, status=200)

    @swagger_auto_schema(request_body=IncomeSerializer)
    def put(self, request, pk):
        income = get_object_or_404(Income, id=pk, user=request.user)
        serializer = IncomeSerializer(income, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        income = get_object_or_404(Income, id=pk, user=request.user)
        account = income.account
        if account.balance < income.amount:
            return Response(
                {"detail": "Bu daromad allaqachon sarflangan, uni o'chirib bo'lmaydi."},
                status=400,
            )
        with transaction.atomic():
            account.balance -= income.amount
            account.save(update_fields=['balance'])
            income.delete()
        return Response(status=204)









