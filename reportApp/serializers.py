# report/serializers.py

from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'user', 'level', 'title', 'description', 'created_date']
        read_only_fields = ['id', 'user', 'created_date']
