#api/serializers.py
import base64
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import serializers

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

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserSerializer):
    """Сериализатор создания юзера."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name'
        )

class CustomUserSerializer(UserSerializer):
    """Информация по юзерам/юзеру."""
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


class RecipeIngredientAmountSerializer2(serializers.ModelSerializer):
    # id = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField()
    # id = serializers.CharField(source='ingredient.id')
    # amount = serializers.IntegerField()
    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'amount', )


class RecipeSerializerWrite(serializers.Serializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientAmountSerializer2(many=True, required=True)
    image = Base64ImageField(required=True, allow_null=False)
    name = serializers.CharField()
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(read_only=False)
    # print(ingredients)
    
    class Meta:
        model = Recipe
        fields = (
        'id', 'tags', 'author', 'ingredients', 
        'is_favorited', 'is_in_shopping_cart', 'name', 'image',  'text', 'cooking_time', 
    )
    




    def create(self, validated_data):
        # print(validated_data)
        # print(serializers.initial_data)
        # raise Exception(777)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        # print(recipe)
        # print(ingredients)
        
        # raise Exception(777)
        for ingredient in ingredients:
            instance_ingredient = Ingredient.objects.get(id=ingredient['id'])
            # print(ingredient['amount'])
            RecipeIngredientAmount.objects.create(
                recipe=recipe,
                ingredient=instance_ingredient,
                amount=ingredient['amount']
            )
        for tag in tags:
            print(recipe)
            recipe.tags.add(tag)
            print(tag)

        # raise Exception(777)
        return recipe
            # print(ingredient) 
            # print(ingredient['id'])
            # print(ingredient['amount'])
            # raise Exception(ingredient)
            # raise Exception(777)
        # print(tags)
        # recipe.tags.add(t1, t2, t3)
    
    def to_representation(self, instance):
        return RecipeSerializer(instance,
        context={'request': self.context.get('request')}).data

 
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)




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
    """Подписка и отписка от user_id."""
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


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
