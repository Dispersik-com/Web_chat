from django.shortcuts import redirect
from .models import UserProfile

from django.shortcuts import redirect
from django.urls import reverse


# Клас для виконання коду перед викликом кожної функції представлення
# class MiddlewareClass:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#         return response