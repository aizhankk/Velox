from rest_framework import serializers
from .models import Task, Category, UserAccount
from django.utils import timezone
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'name', 'password')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['user']

    def validate_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("The date cannot be in the past")
        return value

    def validate(self, data):
        start = data.get('time_start')
        end = data.get('time_end')
        if start and end and end <= start:
            raise serializers.ValidationError({
                'time_end': 'The end time must be later than the start time'
            })
        return data

    def create(self, validated_data):
        category = validated_data.pop('category', None)  
        user = self.context['request'].user

        if category and category.user != user:
            raise serializers.ValidationError("Category does not belong to the user")

        validated_data['category'] = category
        validated_data['user'] = user
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        category = validated_data.pop('category', None)
        user = self.context['request'].user

        if category and category.user != user:
            raise serializers.ValidationError("Category does not belong to the user")

        if category is not None:
            instance.category = category

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class UserTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['wake_up_time', 'sleep_time']
