#api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.authtoken import views

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet, 
    SubscriptionViewSet, 
    # SubscrbeViewSet,
    APISubscribe,
    FavoriteViewSet,
    CartViewSet
    )

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)
v1_router.register('recipes', RecipeViewSet, basename='recipes')
# v1_router.register('recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet.as_view(), basename='favorite')
v1_router.register(r'users/subscriptions', SubscriptionViewSet, basename='subscriptions')
# v1_router.register(r'users/(?P<user_id>\d+)/subscribe', SubscrbeViewSet, basename='subscribe')


urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path(r'users/<int:user_id>/subscribe/', APISubscribe.as_view(
        {'post': 'create', 'delete': 'destroy'})),
    path(r'recipes/<int:recipe_id>/favorite/', FavoriteViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'})),
    path(r'recipes/<int:recipe_id>/shopping_cart/', CartViewSet.as_view(
        {'get':'list', 'post': 'create', 'delete': 'destroy'})),
    # path(r'recipes/<int:recipe_id>/shopping_cart/', CartViewSet.as_view(
    #     {'get':'list', 'post': 'create', 'delete': 'destroy'})),

    # path('', include('.users.urls')),
    # path('', include('djoser.urls')),
    # path('', include('djoser.urls.jwt')),
    # path('api-token-auth/', views.obtain_auth_token),
]

