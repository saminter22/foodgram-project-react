#api/serializers.py
import base64
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import CustomUser
from dish.models import (
    Tag, 
    Ingredient, 
    Recipe, 
    RecipeIngredientAmount, 
    Subscription, 
    Favorite, 
    Cart
    )


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
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name'
        )

class CustomUserSerializer(UserSerializer):
    """Информация по юзерам/юзеру."""
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 
        'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        is_subscribed = Subscription.objects.filter(
            subscriber=self.context.get('request').user, author=obj).exists()
        return is_subscribed


class TagSerializer(serializers.ModelSerializer):
    """Возвращает список тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Возвращает список ингредиентов."""
    measurement_unit = serializers.CharField(source='measurement')
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    """Возвращает количество ингредиентов, связанных с ингредиентом и рецептом."""
    id = serializers.CharField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement')
    amount = serializers.CharField()
    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class AuthorSerializer(serializers.ModelSerializer):
    """Информация по автору для показе в рецепте."""
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
        # is_subscribed = Subscription.objects.filter(user=obj.id, author=obj.id).exists()
            return Subscription.objects.filter(
            subscriber=user, author=obj).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    """Показывает список рецептов."""
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
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Cart.objects.filter(user=user, recipe=obj.id).exists()
        return False


class IngredientAmountSerializerWrite(serializers.ModelSerializer):
    """Принимает количество ингредиента и его id при записи рецепта."""
    id = serializers.IntegerField()
    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'amount', )


class RecipeSerializerWrite(serializers.ModelSerializer):
    """Принимает данные для записи рецепта."""
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientAmountSerializerWrite(many=True, required=True)
    image = Base64ImageField(required=True, allow_null=False)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = (
        'id', 'tags', 'author', 'ingredients', 
        'name', 'image',  'text', 'cooking_time', 
        )
        # У каждого автора рецепты с ункальными названиями
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author')
            )
        ]

    # def validate(self, data):
    #     # print(data)
    #     # print(len(data['tags']))
    #     if len(data['tags']) == 0:
    #         raise serializers.ValidationError(
    #             'Теги обязательны!'
    #         )
    #     return data

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError('Должен быть хотя бы один ингредиент!')
        return value

    def validate_tags(self, value):
        # print(value)
        for item in value:
            if not Tag.objects.filter(name=item).exists():
                raise serializers.ValidationError('Теги обязательны!')
        return value

    def to_representation(self, instance):
        return RecipeSerializer(instance,
        context={'request': self.context.get('request')}).data

    def add_ingredients(self, recipe, ingredients):
        # print(recipe)
        for ingredient in ingredients:
            id_ingredient = Ingredient.objects.get(id=ingredient['id'])
            RecipeIngredientAmount.objects.create(
                recipe=recipe,
                ingredient=id_ingredient,
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe
 
    def update(self, instance, validated_data):
        recipe = instance
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredientAmount.objects.filter(recipe=instance).delete()
        self.add_ingredients(recipe, ingredients)
        return instance


# class SubscriptionSerializer(serializers.ModelSerializer):
#     """Показывает список подписчиков."""
#     class Meta:
#         model = CustomUser
#         fields = ('email', 'id', 'username', 'first_name', 'last_name', )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Показывает короткую информамцию по рецепту."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка и отписка от user_id."""
    recipes = ShortRecipeSerializer(many=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 
            'is_subscribed', 
            'recipes', 
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=user, author=obj.id).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    """Выдает данные по рецепту при подписке."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
