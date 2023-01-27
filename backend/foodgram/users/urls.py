#users/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.authtoken import views

app_name = 'users'


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
]
