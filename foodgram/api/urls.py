from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet,
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionViewSet,
    APISubscribe,
)

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register(
    'users/subscriptions',
    SubscriptionViewSet, basename='subscriptions')
v1_router.register('users', CustomUserViewSet, basename='users')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
urlpatterns = [
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(r'users/<int:user_id>/subscribe/', APISubscribe.as_view(
        {'post': 'create', 'delete': 'destroy'})),

]
