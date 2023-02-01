#api/views.py

from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import IntegrityError
from django.db.models import Sum
from django.shortcuts import render
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import viewsets
from rest_framework import permissions
from djoser.views import UserViewSet
from dish.models import (
    Tag, Ingredient, Recipe, RecipeIngredientAmount,
    Subscription,
    Favorite
    )
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    TagSerializer, IngredientSerializer, RecipeSerializer,
    SubscriptionSerializer, 
    SubscribeSerializer,
    FavoriteSerializer
)
# from users.models import User
from django.contrib.auth import get_user_model
from .permissions import IsAuthenticated
from .mixins import CreateDestroyViewSet, ListCreateDestroyViewSet

User = get_user_model()


class CustomUserCreateViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer



class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
#     @action()




class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    # @action(detail=True, methods=['post'], name='favorite')
    # def favorite(self, request, pk=None):
    #     user = self.get_object()
    #     serializer = FavoriteSerializer(data=request.data)
    #     if serializer.is_valid():
    #         user.favorite__recipe = pk 

    @action(detail=False, )
    def download_shopping_cart(self, request):
        user = request.user
        # recipes = Recipe.objects.select_related().filter(cart__user=user)
        # print(recipes.query)
        # ingredients = Ingredient.objects.filter(recipes__cart__user=user)
        # print(ingredients)
        cartingredients=RecipeIngredientAmount.objects.filter(
            recipe__cart__user=user).order_by('-ingredient', '-amount').select_related(
                'ingredient','recipe').annotate(Sum('amount'))
        # cartingredients = cartingredients.values('ingredient').annotate(Sum('amount'))
        print(cartingredients)
        # cartingredients = cartingredients.aggregate(Sum('amount'))
        with open('list_of_buy.txt', 'w') as file:
            file.write('Список покупок FoodGram:\n\n')
            for item in cartingredients:
                file.write(
                    f'{item.ingredient} - {item.amount}\n'
                )
            file.write('\nУдачных покупок!\n')

        # ingredientsamount = RecipeIngredientAmount.objects.filter(
        #     ingredient=ingredients)
        # print(ingredientsamount)
        return Response (
                {'message': 'Список покупок сформирован'},
                status=status.HTTP_200_OK
                )

        




class SubscriptionViewSet(viewsets.ModelViewSet):
    """Показываем текущие подписки."""
    serializer_class = SubscriptionSerializer
    def get_queryset(self):
        return User.objects.filter(subscribers__subscriber=self.request.user)
        # return self.request.user.authors




# class SubscrbeViewSet(viewsets.ModelViewSet):
#     permission_classes = (IsAuthenticated, )
#     # queryset = Subscription.objects.all()
#     serializer_class = SubscribeSerializer
    
#     def get_queryset(self):
#         user_id = self.kwargs.get('user_id')
#         subscribers = User.objects.filter(id=user_id).authors.all()
#         return subscribers


class APISubscribe(CreateDestroyViewSet):
    """Подписка, отписка."""
    permission_classes = (IsAuthenticated, )

    def destroy(self, request, user_id):
        subscribe = Subscription.objects.filter(subscriber=request.user, author__id=user_id)
        if not subscribe:
            return Response(
                {'message': 'Такой подписки нет'}, 
                status=status.HTTP_404_NOT_FOUND
                )
        subscribe.delete()
        return Response({'message': 'Отписка произошла'}, status=status.HTTP_204_NO_CONTENT)

    def create(self, request, user_id):
        author = get_object_or_404(User, pk=user_id)
        user = request.user
        if not author:
            return Response(
                {'message': 'Такого автора нет'},
                status=status.HTTP_404_NOT_FOUND
                )
        if author == user:
            return Response(
                {'message': 'Подписаться на себя нельзя'},
                status=status.HTTP_400_BAD_REQUEST
                )
        try:
            Subscription.objects.create(subscriber=request.user, author=author)
            serializer = SubscribeSerializer(author, context = {'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {'message': 'Подписка уже оформлена'}, 
                status=status.HTTP_400_BAD_REQUEST
                )


class FavoriteViewSet(CreateDestroyViewSet):
    """Избранное - добавление, удаление."""
    permission_classes = (IsAuthenticated, )

    def create(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        try:
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe, context = {'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except  IntegrityError:
            return Response(
                {'message': 'Уже добавлено в Избранное'}, 
                status=status.HTTP_400_BAD_REQUEST
                )

    def destroy(self, request, recipe_id):
        user = request.user
        favorite = Favorite.objects.filter(user=user, recipe=recipe_id)
        if not favorite:
            return Response(
            {'message': 'Рецепт отсутствует в избранномм'}, status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(
            {'message': 'Убрано из Избранного'}, status=status.HTTP_204_NO_CONTENT
            )


class CartViewSet(ListCreateDestroyViewSet):
    """Корзина - добавление, удаление, вывод ингредиентов."""
    permission_classes = (IsAuthenticated, )

    def destroy(self, request, recipe_id):
        user = request.user
        favorite = Favorite.objects.filter(user=user, recipe=recipe_id)
        if not favorite:
            return Response(
            {'message': 'Рецепт отсутствует в корзине'}, status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(
            {'message': 'Удалено из корзины'}, status=status.HTTP_204_NO_CONTENT
            )

    def create(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        try:
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe, context = {'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except  IntegrityError:
            return Response(
                {'message': 'Уже в корзине'}, status=status.HTTP_400_BAD_REQUEST
                )

    def list(self, request):
        ...
