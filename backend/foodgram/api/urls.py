#api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import (
    CustomUserViewSet,
    TagViewSet, 
    # IngredientViewSet, 
    # RecipeViewSet, 
    # SubscriptionViewSet, 
    # # SubscrbeViewSet,
    # APISubscribe,
    # FavoriteViewSet,
    # CartViewSet
    )

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # path('api-token-auth/', views.obtain_auth_token),
]
