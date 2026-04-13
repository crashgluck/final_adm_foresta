from rest_framework import serializers

from apps.finance.models import CommonExpenseDebt, FinancialMovement, PaymentAgreement, ServiceDebt, UnpaidFine


class CommonExpenseDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonExpenseDebt
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at')


class ServiceDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDebt
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at')


class PaymentAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAgreement
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at')


class UnpaidFineSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnpaidFine
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at')


class FinancialMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialMovement
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at')

