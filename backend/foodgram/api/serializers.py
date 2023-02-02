#api/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserSerializer

from dish.models import (
    Tag, 
    Ingredient, 
    Recipe, 
    RecipeIngredientAmount, 
    Subscription, 
    Favorite, 
    Cart
    )

User = get_user_model()

class CustomUserCreateSerializer(UserSerializer):
    """Сериализатор создания юзера."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name'
        )

class CustomUserSerializer(UserSerializer):
    """Информация по юзерам."""
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 
        'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        is_subscribed = Subscription.objects.filter(
            subscriber=self.context.get('request').user, author=obj).exists()
        return is_subscribed


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source='measurement')
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement')
    amount = serializers.CharField()
    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount', )

class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        # is_subscribed = Subscription.objects.filter(user=obj.id, author=obj.id).exists()
        is_subscribed = Subscription.objects.filter(
            subscriber=self.context.get('request').user, author=obj).exists()
        return is_subscribed

class RecipeSerializer(serializers.ModelSerializer):
    """Показываем рецепты."""
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer()
    ingredients = RecipeIngredientAmountSerializer(source='recipeingredientamount_set', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 
            'is_favorited', 'is_in_shopping_cart', 'name', 'image',  'text', 'cooking_time', 
        )

    def get_is_favorited(self, obj):
        is_favorited = Favorite.objects.filter(
            user=self.context.get('request').user, recipe=obj).exists()
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        is_in_shopping_cart = Cart.objects.filter(
            user=self.context.get('request').user, recipe=obj).exists()
        return is_in_shopping_cart

class SubscriptionSerializer(serializers.ModelSerializer):
    """Показываем список подписчиков."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', )

class ShortRecipeSerializer(serializers.ModelSerializer):
    """Показываем короткую информамцию по рецепту."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка и отписка от user_id"""
    recipes = ShortRecipeSerializer(many=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 
            'is_subscribed', 
            'recipes', 
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate_following(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError("Нельзя подписаться на себя!")
        return value

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
