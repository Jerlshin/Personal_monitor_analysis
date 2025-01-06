from rest_framework import serializers
from .models import CalendarTask, TodoTask

class CalendarTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarTask
        fields = '__all__'

class TodoTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoTask
        fields = '__all__'
