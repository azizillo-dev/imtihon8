from rest_framework import serializers


class ReportDateSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)


class CurrencySerializer(serializers.Serializer):
    currency = serializers.ChoiceField(choices=['UZS', 'USD', 'EUR'], default='UZS')


class ReportMonthSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=False, min_value=2000, max_value=2100)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)


class ReportFilterSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, data):
        if data.get('date_from') and data.get('date_to') and data['date_from'] > data['date_to']:
            raise serializers.ValidationError("date_from sanasi date_to dan katta bo'lishi mumkin emas.")
        return data
