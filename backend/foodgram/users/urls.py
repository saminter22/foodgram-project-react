#users/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.authtoken import views
from django.urls import re_path
from djoser import views
# from rest_framework_simplejwt import views


app_name = 'users'


urlpatterns = [
    # path('', include('djoser.urls.authtoken')),
    # path('', include('djoser.urls.jwt')),
    # re_path(r"^auth/token/login/?$", views.TokenCreateView.as_view(), name="login"),
    # re_path(r"^auth/token/logout/?$", views.TokenDestroyView.as_view(), name="logout"),
]
