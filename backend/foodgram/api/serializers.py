#api/serializers.py
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from dish.models import Tag, Ingredient, Recipe, RecipeIngredientAmount
# from users.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement')

class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.id')
    measurement = serializers.CharField(source='ingredient.id')
    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'name', 'amount', 'measurement', )


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement = serializers.CharField(source='ingredient.measurement')
    amount = serializers.CharField()
    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'name', 'amount', 'measurement', )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    # ingredients = IngredientSerializer(many=True, read_only=True)
    # ingredients = RecipeIngredientAmountSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientAmountSerializer(source='recipeingredientamount_set', many=True)
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'image',  'name', 'text', 'cooking_time')