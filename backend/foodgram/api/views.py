#api/views.py
from django.shortcuts import render

from rest_framework import viewsets
from djoser.views import UserViewSet
from dish.models import Tag, Ingredient, Recipe, RecipeIngredientAmount
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, RecipeIngredientAmountSerializer
# from users.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

# class RecipeIngredientAmountSViewSet(viewsets.ModelViewSet):
#     queryset = RecipeIngredientAmount.objects.all()
#     serializer_class = RecipeIngredientAmountSerializer

#     def get_queryset(self):
#         recipe = Recipe.
#         return recipe.

    
    # def get_queryset(self):
    #     title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
    #     return title.reviews.all()