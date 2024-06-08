# report/models.py
from django.db import models
from userApp.models import CustomUser

class Report(models.Model):
    LEVEL_CHOICES = (
        ('unit', 'Unit Level'),
        ('department', 'Department Level'),
        ('division', 'Division Level'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Correct field name
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
