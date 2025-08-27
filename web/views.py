from django.shortcuts import render

# web/views.py
from django.http import JsonResponse

def home(request):
    return JsonResponse({"django": "hello"})
