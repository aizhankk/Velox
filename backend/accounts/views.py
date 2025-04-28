from django.shortcuts import render
from .models import Task
from .serializers import TaskSerializer
from rest_framework import filters, viewsets

class TaskViewSet(viewsets.ModelViewSet):
    
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['title', 'category', 'notes']
    ordering_fields  = ['date', 'time', 'created_at']
