#api/views.py
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import Sum
from django.http import FileResponse
from django.http import HttpResponse
from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet

from django_filters.rest_framework import (
    DjangoFilterBackend, FilterSet, AllValuesMultipleFilter, NumberFilter, BooleanFilter,
    ModelMultipleChoiceFilter
)

from .permissions import IsAuthenticated, IsAuthorOrReadOnly
from .mixins import CreateDestroyViewSet, ListCreateDestroyViewSet

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
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    TagSerializer, 
    IngredientSerializer, 
    RecipeSerializer,
    RecipeSerializerWrite,
    # SubscriptionSerializer, 
    FavoriteSerializer,
    SubscribeSerializer,
)


class CustomUserCreateViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    # permission_classes = (IsAuthorOrReadOnly, )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('id', )
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    # filter_backends = (filters.SearchFilter, )
    # search_fields = ('^name', )
    pagination_class = None

    def get_queryset(self):
        if self.request.GET.get('name'):
            name = self.request.GET.get('name')
            queryset = Ingredient.objects.filter(name__startswith=name)
            return queryset
        return Ingredient.objects.all()


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
        # lookup_type='in'
    )
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_in_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 
            # 'author', 
            # 'tags_filter'
            )

    def filter_is_favorited(self, queryset, name, value):
        # print(name)
        queryset = Recipe.objects.all()
        user = self.request.user
        if value:
            queryset = queryset.filter(favorite__user=user)
        return queryset

    def filter_in_cart(self, queryset, name, value):
        queryset = Recipe.objects.all()
        user = self.request.user
        if value:
            queryset = queryset.filter(cart__user=user)
        return queryset

    # def filter_is_favorited(self, queryset, name, value):
    #     if value:
    #         user = self.request.user
    #         queryset = user.favorite.all()
    #     return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Контроллер рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filter_backends = (DjangoFilterBackend, )
    # filter_backends = (filters.SearchFilter, )
    filterset_class = RecipeFilter
    search_fields = ('ingredients', )

    def get_queryset(self):
        if self.request.GET.get('tags'):
            queryset = Recipe.objects.all()
            tags = self.request.GET.get('tags')
            # print(tags)
            queryset = queryset.filter(tags__slug=tags)
            return queryset
        return Recipe.objects.all()

    def get_permissions(self):
        """Права на разные запросы."""
        if self.action in (
            'create', 'favorite', 'shopping_cart', 'download_shopping_cart'):
            self.permission_classes = (IsAuthenticated, )
        elif self.request.method == 'PATCH':
            self.permission_classes = (IsAuthorOrReadOnly, )
        elif self.action in ('retrieve', ):
            self.permission_classes = (permissions.AllowAny, )
            # self.permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
        self.permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeSerializerWrite

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # serializer.save(author=self.request.user)
        super().perform_update(serializer)

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
        file_handle = file.open()
        response = HttpResponse(file_handle, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=buy_list.txt'
        return response

        # with open(file,'r') as file2:
        #     response = HttpResponse(file2, content_type='text/plain')
        #     response['Content-Disposition'] = 'attachment; filename=buy_list.txt'
        # return Response
        # # return Response (
        # #         {'message': 'Список покупок сформирован'},
        # #         status=status.HTTP_200_OK
        # #         )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Показываем текущие подписки."""
    # serializer_class = SubscriptionSerializer
    serializer_class = SubscribeSerializer
    # pagination_class = None

    def get_queryset(self):
        return CustomUser.objects.filter(subscribers__subscriber=self.request.user)


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
        author = get_object_or_404(CustomUser, pk=user_id)
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
