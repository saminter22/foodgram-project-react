#api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.authtoken import views

from .views import TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)
v1_router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    # path('', include('.users.urls')),
    # path('', include('djoser.urls')),
    # path('', include('djoser.urls.jwt')),
    # path('api-token-auth/', views.obtain_auth_token),
]

