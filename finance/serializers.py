from django.db import transaction
from rest_framework import serializers

from .models import Account, Expense, ExpenseCategory, Income, IncomeCategory


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'user', 'name', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_name(self, value):
        user = self.context['request'].user
        categories = ExpenseCategory.objects.filter(user=user, name__iexact=value)
        if self.instance:
            categories = categories.exclude(id=self.instance.id)
        if categories.exists():
            raise serializers.ValidationError("Bu nomdagi chiqim kategoriyasi allaqachon mavjud.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return ExpenseCategory.objects.create(user=user, **validated_data)


class IncomeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeCategory
        fields = ['id', 'user', 'name', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_name(self, value):
        user = self.context['request'].user
        categories = IncomeCategory.objects.filter(user=user, name__iexact=value)
        if self.instance:
            categories = categories.exclude(id=self.instance.id)
        if categories.exists():
            raise serializers.ValidationError("Bu nomdagi kirim kategoriyasi allaqachon mavjud.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return IncomeCategory.objects.create(user=user, **validated_data)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Balans manfiy bo'lishi mumkin emas.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        account = Account.objects.create(user=user, **validated_data)
        return account



class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'user', 'account', 'category', 'amount', 'description', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Xarajat miqdori musbat bo'lishi kerak.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        if attrs['account'].user_id != user.id:
            raise serializers.ValidationError("Bu hisob sizga tegishli emas.")
        if attrs['category'].user_id != user.id:
            raise serializers.ValidationError("Bu kategoriya sizga tegishli emas.")
        available = attrs['account'].balance
        # tahrirlashda eski summa shu hisobga qaytadi
        if self.instance and self.instance.account_id == attrs['account'].id:
            available += self.instance.amount
        if available < attrs['amount']:
            raise serializers.ValidationError("Hisobda mablag' yetarli emas.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        account = validated_data['account']
        with transaction.atomic():
            account.balance -= validated_data['amount']
            account.save(update_fields=['balance'])
            expense = Expense.objects.create(user=user, **validated_data)
        return expense

    def update(self, instance, validated_data):
        with transaction.atomic():
            old_account = instance.account
            old_account.balance += instance.amount
            old_account.save(update_fields=['balance'])

            new_account = validated_data['account']
            new_account.refresh_from_db()
            new_account.balance -= validated_data['amount']
            new_account.save(update_fields=['balance'])
            return super().update(instance, validated_data)


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['id', 'user', 'account', 'category', 'amount', 'description', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Daromad miqdori musbat bo'lishi kerak.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        if attrs['account'].user_id != user.id:
            raise serializers.ValidationError("Bu hisob sizga tegishli emas.")
        if attrs['category'].user_id != user.id:
            raise serializers.ValidationError("Bu kategoriya sizga tegishli emas.")
        if self.instance:
            # eski summa olib tashlansa, hisob manfiy bo'lib qolmasligi kerak
            balance_after = self.instance.account.balance - self.instance.amount
            if self.instance.account_id == attrs['account'].id:
                balance_after += attrs['amount']
            if balance_after < 0:
                raise serializers.ValidationError("Bu daromad allaqachon sarflangan, uni bunday o'zgartirib bo'lmaydi.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        account = validated_data['account']
        with transaction.atomic():
            account.balance += validated_data['amount']
            account.save(update_fields=['balance'])
            income = Income.objects.create(user=user, **validated_data)
        return income

    def update(self, instance, validated_data):
        with transaction.atomic():
            old_account = instance.account
            old_account.balance -= instance.amount
            old_account.save(update_fields=['balance'])

            new_account = validated_data['account']
            new_account.refresh_from_db()
            new_account.balance += validated_data['amount']
            new_account.save(update_fields=['balance'])
            return super().update(instance, validated_data)
