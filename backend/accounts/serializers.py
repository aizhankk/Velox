from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from .models import Task
from rest_framework import serializers
from django.utils import timezone

User = get_user_model()
class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'name', 'password')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def validate_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("The date cannot be in the past")
        return value
    
    def validate(self, data):
        start = data.get('time_start')
        end   = data.get('time_end')
        if start and end and end <= start:
            raise serializers.ValidationError({
                'time_end': 'The end time must be later than the start time'
            })
        return data



