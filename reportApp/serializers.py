from rest_framework import serializers
from .models import Report

from userApp.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'username', 'email']  # Add other fields if needed

class ReportSerializer(serializers.ModelSerializer):
    created_by = CustomUserSerializer()  # Nest the CustomUserSerializer
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'created_by', 'level', 'title', 'description', 'created_date', 'status', 'status_display']
        read_only_fields = ['id', 'created_by', 'created_date']

    def get_status_display(self, obj):
        return 'approved' if obj.status else 'pending'
        
        
        
class ReportUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'title', 'description', 'status']