#api/views.py
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import Sum
from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet

from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsAuthenticated, IsAuthorOrReadOnly
from .mixins import CreateDestroyViewSet, ListCreateDestroyViewSet

from dish.models import (
    Tag, 
    Ingredient, 
    Recipe, 
    RecipeIngredientAmount,
    Subscription,
    Favorite,
    Cart
    )
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    TagSerializer, 
    IngredientSerializer, 
    RecipeSerializer,
    RecipeSerializerWrite,
    SubscriptionSerializer, 
    FavoriteSerializer,
    SubscribeSerializer,
)

User = get_user_model()

class CustomUserCreateViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    # permission_classes = (IsAuthorOrReadOnly, )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('name', )


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', ) 


class RecipeViewSet(viewsets.ModelViewSet):
    """Работа с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('tags', 'author', )
    # pagination_class = None 

    def get_permissions(self):
        """Права на разные запросы."""
        if self.action in (
            'create', 'favorite', 'shopping_cart', 'download_shopping_cart'):
            self.permission_classes = (IsAuthenticated, )
        self.permission_classes = (permissions.IsAuthenticatedOrReadOnly)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeSerializerWrite

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'], 
        detail=True, 
        permission_classes=(IsAuthenticated, ),
        # filter_backends = (DjangoFilterBackend, ),
        # filterset_fields = ('tags', )
    )
    def favorite(self, request, **kwargs):
        """Избранное - добавление, удаление."""
        recipe_id = self.kwargs.get('pk')
        user = self.request.user
        if request.method == 'POST':
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
        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe_id)
            if not favorite:
                return Response(
                {'message': 'Рецепт отсутствует в избранномм'}, status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(
                {'message': 'Убрано из Избранного'}, status=status.HTTP_204_NO_CONTENT
                )

    @action(methods=['POST', 'DELETE'], detail=True, permission_classes=(IsAuthenticated, ))
    def shopping_cart(self, request, **kwargs):
        """Корзина - добавление, удаление."""
        recipe_id = self.kwargs.get('pk')
        user = self.request.user
        if request.method == 'POST':
            recipe = Recipe.objects.filter(pk=recipe_id)
            if not recipe:
                return Response(
                    {'message': 'Такого рецепта нет'},
                    status=status.HTTP_404_NOT_FOUND
                    )
            recipe = get_object_or_404(Recipe, id=recipe_id)
            try:
                Cart.objects.create(user=user, recipe=recipe)
                serializer = FavoriteSerializer(recipe, context = {'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {'message': 'Уже в корзине'}, status=status.HTTP_400_BAD_REQUEST
                    )
        if request.method == 'DELETE':
            cart = Cart.objects.filter(user=user, recipe=recipe_id)
        if not cart:
            return Response(
            {'message': 'Рецепт отсутствует в корзине'}, status=status.HTTP_400_BAD_REQUEST
            )
        cart.delete()
        return Response(
            {'message': 'Удалено из корзины'}, status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, )
    def download_shopping_cart(self, request):
        """Список покупок в файл."""
        user = request.user
        # recipes = Recipe.objects.select_related().filter(cart__user=user)
        # print(recipes.query)
        cartingredients=RecipeIngredientAmount.objects.filter(
            recipe__cart__user=user).order_by('-ingredient', '-amount').select_related(
                'ingredient','recipe')
        # print(cartingredients)
        with open('buy_list.txt', 'w') as file:
            file.write('Список покупок FoodGram:\n\n')
            for item in cartingredients:
                file.write(
                    f'{item.ingredient} - {item.amount}\n'
                )
            file.write('\nУдачных покупок!\n')
        return Response (
                {'message': 'Список покупок сформирован'},
                status=status.HTTP_200_OK
                )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Показываем текущие подписки."""
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return User.objects.filter(subscribers__subscriber=self.request.user)


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
